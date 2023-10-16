from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from src.database.schemas import UserCreate
from src.dependencies import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.database.services.crud import UserCRUDService, get_user_service
from src.config.config import settings
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
    print(payload)
    response = requests.post(
        f"{settings.auth_server_url}/signup?service=arcade&redirect_url=/auth/login",
        data=payload
    )
    if response.status_code == 409:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email address or username already registered.")
    new_user = UserCreate(
        username=form_data.username,
        public_id=response.json()['public_id']
    )
    db_obj = user_crud_service.create(new_user)
    return {"msg": "User Created"}


@router.post("/auth/login", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: Session = Depends(get_db)):
    payload = {'username': form_data.username,
               'password': form_data.password}
    response = requests.post(
        f"{settings.auth_server_url}/auth?service=arcade",
        data=payload
    )
    if response.status_code == 403:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="Email address not verified, please check your inbox for a verification link!")
    if response.status_code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Username or password incorrect, please try again.")
    return {'access_token': response.json(), "token_type": "bearer"}
