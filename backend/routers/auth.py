from typing import Annotated
from utils.schema import UsrInDB, Token, TokenData, User
from fastapi import Depends, FastAPI, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta,timezone
from functools import lru_cache
from utils.config import Settings
from utils.db_helper import connect_to_db
from typing import Optional
router = APIRouter()


@lru_cache
def get_settings():
    return Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Verifies if a plain text password matches a hashed password
# Returns True if passwords match, False otherwise
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Generates a hashed version of a plain text password
# Returns the hashed password string
def get_password_hash(password):
    return pwd_context.hash(password)

# Retrieves a user from the database by username
# Returns a UsrInDB object if found, None otherwise
def get_user(email: str):
    conn = connect_to_db()

    try:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()
    finally:
        conn.close()

# Authenticates a user by verifying username and password
# Returns the user object if authentication successful, False otherwise
def  authenticate_user( email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

# this function is used to create access token
# it takes in settings, data, expires_delta and auth_method as arguments
# returns the encoded jwt token
def create_access_token(settings, data: dict, expires_delta: Optional[timedelta] = None, auth_method="password"):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire, "auth_method": auth_method})  # Include auth method
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Verifies the token and returns the user and auth method
async def get_current_user(
    settings: Annotated[Settings, Depends(get_settings)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email = payload.get("sub")
        auth_method = payload.get("auth_method", "google")

        if email is None:
            raise credentials_exception

        user = get_user(email)

        if user is None:
            raise credentials_exception

        return {
            "user": user,
            "auth_method": auth_method
        }

    except InvalidTokenError:
        raise credentials_exception

# Verifies if a user is active (not disabled)
# Raises HTTPException if user is disabled, otherwise returns the user
async def get_current_active_user(
    current_user_data: Annotated[dict, Depends(get_current_user)]
):
    user = current_user_data["user"]
    auth_method = current_user_data["auth_method"]

    if user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return {
        "user": user,
        "auth_method": auth_method
    }

