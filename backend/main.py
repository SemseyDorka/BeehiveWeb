from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os
from groq import Groq
from dotenv import load_dotenv
import mongo as db
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

@app.get("/api/meresek")
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
@app.get("/api/meresek")
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
          
@app.post("/api/transcribe")
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