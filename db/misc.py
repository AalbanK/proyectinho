from .database import SessionLocal
def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# https://www.freecodecamp.org/news/how-to-add-jwt-authentication-in-fastapi/
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext


load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutos
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 días
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')   # en el archivo .env
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')    # en el archivo .env  

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hasheado(password: str):
    return password_context.hash(password)

def verificar_password(password: str, hashed_pass: str):
    try:
        print(password_context.verify(password, hashed_pass))
    
    except:
        print("An exception occurred") 
    
    return password_context.verify(password, hashed_pass)  

def crear_access_token(subject: Union[str, Any], expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def crear_refresh_token(subject: Union[str, Any], expires_delta: int = None):
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt