from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
from groq import Groq
from dotenv import load_dotenv
import mongo as db
from pydantic import BaseModel
client=Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()
#todo: cors-ot szigorítani!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='root',
        password=os.environ.get('DB_PASSWORD'), 
        database=os.environ.get('DB_NAME', 'beehive_db'), 
        cursorclass=pymysql.cursors.DictCursor
    )


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
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=400
        )
        result = chat_completion.choices[0].message.content
        return {"analysis": result}
        db.save_entry(data.text, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))