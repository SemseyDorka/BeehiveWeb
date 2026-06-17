import os
from dotenv import load_dotenv
import pymongo
import certifi
from datetime import datetime
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")



if mongo_uri:
    print(f"Success :)")
else:
    print("ERROR: empty MONGO_URI")

def get_database():
    if not mongo_uri:
            raise ValueError("No MONGO_URI .env variable")
            
    client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where())
    return client["mehesz_projekt_db"]

def save_entry(tartalom, elemzes):
    try:
        db = get_database()
        collection = db["naplo_bejegyzesek"]
        
        document = {
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tartalom": tartalom,
            "elemzes": elemzes,
            "created_at": datetime.utcnow()  
        }
        
        collection.insert_one(document)
    except Exception as e:
        print(f"Db save error: {e}")

def get_entries():
    try:
        db = get_database()
        collection = db["naplo_bejegyzesek"]
        

        cursor = collection.find().sort("created_at", -1)
        return list(cursor)
    except Exception as e:
        return []
