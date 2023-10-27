from fastapi import HTTPException, Depends, status, WebSocket
from jose import jwt, JWTError
from src.database.services.database import SessionLocal
import socketio
import logging
from typing import Any



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('logs/arcade_backend.log')
logger.addHandler(file_handler)





