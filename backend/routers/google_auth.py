from datetime import timedelta
from typing import Annotated
from fastapi import Depends, Request, APIRouter
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import os
import pymysql  
from .auth import create_access_token
from dotenv import load_dotenv
from utils.config import Settings
from functools import lru_cache
from fastapi.responses import RedirectResponse

load_dotenv()

router = APIRouter()


@lru_cache

def get_settings():
    return Settings()

def get_db_connection():
    return pymysql.connect(
        host='db',
        user='root',
        password=os.environ.get('DB_PASSWORD'), 
        database=os.environ.get('DB_NAME', 'beehive_db'), 
        cursorclass=pymysql.cursors.DictCursor
    )
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

@router.get("/auth/google")
async def auth_google(request: Request):
    return await oauth.google.authorize_redirect(request, redirect_uri="https://meteor3.elte.hu/kaptarweb/api/auth/google/callback")


@router.get("/auth/google/callback")
async def google_callback(request: Request, settings: Annotated[Settings, Depends(get_settings)]):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo") or {}

        email = user_info.get("email")  
        name = user_info.get("name")
        given_name = user_info.get("given_name")
        
        username = email.split("@")[0] if email else "unknown_user"

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql_check = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql_check, (email,))
                existing_user = cursor.fetchone()

                if not existing_user:
                    sql_insert = """
                        INSERT INTO users (username, email, given_name, disabled) 
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (username, email, given_name, False))
                    connection.commit() 
        finally:
            connection.close()  
        access_token = create_access_token(
            settings,
            data={"sub": email},
            expires_delta=timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            auth_method="google"
)

        frontend_url = f"https://meteor3.elte.hu/kaptarweb/index.html?token={access_token}"

   
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())  
        return {"error": str(e)}