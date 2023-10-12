from fastapi import HTTPException, Depends, status
from jose import jwt, JWTError
from src.database.services.database import SessionLocal



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




