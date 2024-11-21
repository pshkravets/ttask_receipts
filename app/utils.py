from jose import jwt, JWTError
from bcrypt import hashpw, gensalt
from fastapi import Depends, Security
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models import User, get_db

security = HTTPBearer()


def hash_password(password):
    return hashpw(bytes(password, 'utf-8'), gensalt()).decode('utf-8')


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, 'secret_key', algorithm='HS256')
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, 'secret_key', algorithms='HS256')
        return payload
    except JWTError:
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session=Depends(get_db)):
    token = credentials.credentials
    payload = decode_access_token(token)
    return db.query(User).filter_by(login=payload['sub']).first()


def require_auth(user: dict = Depends(get_current_user)):
    return user
