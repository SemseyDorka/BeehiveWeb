import time
import random
import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://beehiveBackend:8000/meresek")
INTERVAL = int(os.getenv("INTERVAL", "600"))  # Alapértelmezett: 10 perc (600 mp)

print("Kaptármérleg Szimulátor elindult", flush=True)

aktualis_suly = 42.0  #innen indul a tesztadat

while True:
    try:
        #   random ingadozás
        suly_valtozas = random.uniform(-0.15, 0.25)
        aktualis_suly = round(aktualis_suly + suly_valtozas, 2)
        
        if aktualis_suly < 10: aktualis_suly = 42.0 # ne legyen a súly kisebb mint 10
        
        # Hőmérséklet
        homerseklet = round(random.uniform(18.0, 32.0), 1)
        #fészek hőmérséklet valamivel magasabb
        feszek_homerseklet = round(random.uniform(1.0, 3.0), 1)+homerseklet

        payload = {
            "suly": aktualis_suly,
            "homerseklet": homerseklet,
            "feszek_homerseklet":feszek_homerseklet,
            "kaptar": 2
        }

        # POST kérés küldése a backendnek
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        print(f"[KÜLDÉS] Súly: {aktualis_suly} kg | Hőm: {homerseklet} °C Válasz: {response.status_code}", flush=True)

    except Exception as e:
        print(f"[ERROR] : {e}", flush=True)

    time.sleep(INTERVAL)