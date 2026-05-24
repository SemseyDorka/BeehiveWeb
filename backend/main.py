from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI()

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
        password='Cucuka123',
        database='beehive_db',
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