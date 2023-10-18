from fastapi import HTTPException, Depends, status, WebSocket
from jose import jwt, JWTError
from src.database.services.database import SessionLocal
import socketio
from typing import Any



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()







