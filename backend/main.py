from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import mongo as db
from pydantic import BaseModel
client=Groq(api_key=os.getenv("GROQ_API_KEY"))
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, users, google_auth
from typing import Annotated
from fastapi import Depends
from routers import auth

app = FastAPI()
#todo: cors-ot szigorítani!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY"),
    same_site="lax",
    https_only=True
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(google_auth.router)


@app.get("/")
def home():
    return {"message": "Welcome to FastAPI OAuth2 Authentication!"}  

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='root',
        password=os.environ.get('DB_PASSWORD'), 
        database=os.environ.get('DB_NAME', 'beehive_db'), 
        cursorclass=pymysql.cursors.DictCursor
    )
#data model
class HiveData(BaseModel):
    kaptar:int 
    suly: float 
    homerseklet: float
    feszek_homerseklet: float

#mérési adatok küldése az adatbázisnak
@app.post("/meresek")
async def save_data(data: HiveData):
    try:
        connection=get_db_connection()
        with connection.cursor() as cursor:
            sql="""
                INSERT INTO merleg (kaptar, suly, homerseklet, feszek_homerseklet) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql,(data.kaptar,data.suly,data.homerseklet,data.feszek_homerseklet))
            connection.commit()
            connection.close()
            return {"status": "success", "message": "Adat elmentve"} 
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meresek")
def read_meresek():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, kaptar, suly, homerseklet, feszek_homerseklet, datum FROM merleg ORDER BY datum DESC")
            adatok = cursor.fetchall()
        conn.close()
        
        for sor in adatok:
            if sor['datum']:
                sor['datum'] = sor['datum'].strftime('%Y-%m-%d %H:%M:%S')
                
        return adatok
    except Exception as e:
        return {"error": str(e)}

@app.get("/me")
async def get_current_user_info(
    current_user: Annotated[
        dict,
        Depends(auth.get_current_active_user)
    ]
):
    user = current_user["user"]

    return {
        "username": user.get("username"),
        "email": user.get("email"),
        "given_name": user.get("given_name"),
        "role": user.get("role"),
        "picture_url":user.get("picture_url"),
        "apiary_id":user.get("apiary_id")
    }     

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        
        transcription = client.audio.transcriptions.create(
            file=(audio.filename, audio_bytes),
            model="whisper-large-v3-turbo",
            language="hu"
        )
        return {"text": transcription.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class NoteRequest(BaseModel):
    text: str 

@app.post("/analyze")
async def analyze_note(data: NoteRequest):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Empty note")
    system_prompt = """
        SZEMÉLYISÉG (Persona):
        Te egy alapos tudományos imeretekkel rendelkező mesterméhész és állategészségügyi szakértő vagy. 
        Segítesz a terepen dolgozó méhészeknek a terepi jegyzeteik elemzésében. 

        FELADAT ÉS LOGIKA (Chain of Thought):
        Az üzenete elejére ne rakj megszólítást, csak a felsorolt pontokat listázd.
        A választ szigorúan az alábbi lépésekben építsd fel:
        1. ADATOK: Listázd ki a megfigyelt tényeket pontosan az a szöveg szereplejen itt amit a méhész megadott.
        2. ANALÍZIS: Értékeld az összefüggéseket (pl. időjárás vs. hordás, anya állapota vs. fiasítás).
        3. DIAGNÓZIS: Mondd ki, mi a család aktuális állapota.
        4. JAVASLAT: Írj maximum 3 konkrét teendőt fontossági sorrendben.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Itt a jegyzetem az elemzéshez: {data.text}"}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.4,
            max_tokens=600
        )
        result = chat_completion.choices[0].message.content
        return {"analysis": result}
        db.save_entry(data.text, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))