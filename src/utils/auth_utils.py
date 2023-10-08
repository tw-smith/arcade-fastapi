from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.database import crud
from datetime import datetime, timedelta
from jose import jwt, JWTError
from argon2 import PasswordHasher
import argon2.exceptions
from src.config.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_hasher = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str, db):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    try:
        pwd_hasher.verify(user.password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db):
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = token_payload.get("sub")
        if username is None:
            raise auth_exception
    except JWTError:
        raise auth_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise auth_exception
    return user
