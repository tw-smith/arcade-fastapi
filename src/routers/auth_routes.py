from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from src.database.schemas import UserCreate
from src.dependencies import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database.services.crud import UserCRUDService, get_user_service
import requests

router = APIRouter()





class SignupForm:
    def __init__(self,
                 email: str = Form(),
                 username: str = Form(),
                 password: str = Form()):
        self.email = email
        self.username = username
        self.password = password

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def create_user(form_data: Annotated[SignupForm, Depends()],
                      user_crud_service: UserCRUDService = Depends(get_user_service)):
    payload = {'email': form_data.email,
               'username': form_data.username,
               'password': form_data.password}
    response = requests.post(
        'https://auth.tw-smith.me/signup?service=arcade?redirect_url=https://tourtracker.tw-smith.me/auth/login',
        data=payload
    )
    if response.status_code == 400:
        pass
        # TODO pass 400 error to client
    new_user = UserCreate(
        username=form_data.username,
        public_id=response.json()['public_id']
    )
    db_obj = user_crud_service.create(new_user)
    return {"msg": "User Created"}


@router.post("/auth/login", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: Session = Depends(get_db)):
    response = requests.post(
        'https://auth.tw-smith.me/auth?service=arcade',
        data=form_data
    )
    if not response.ok:
        if response.json()['detail'] == 'Account not verified':
            pass #TODO: pass to frontend
        pass #TODO pass to frontend
    return {'access_token': response.json(), "token_type": "bearer"}