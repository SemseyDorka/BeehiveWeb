from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql
import os

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
        # Az os.environ.get() kiolvassa a Docker által átadott titkos jelszót
        password=os.environ.get('DB_PASSWORD'), 
        database=os.environ.get('DB_NAME', 'beehive_db'), # a 'beehive_db' az alapértelmezett, ha nem találná
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