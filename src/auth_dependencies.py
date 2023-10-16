from fastapi import HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
from src.database.services.crud import UserCRUDService, get_user_service
from src.database.models import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl='blah')


async def get_authorised_user(token: Annotated[str, Depends(oauth2_scheme)], user_crud_service: UserCRUDService = Depends(get_user_service)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    if token is None:
        print('token is none')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token is none"
        )
    try:
        payload = jwt.decode(token, key='', options={'verify_signature': False})
        print(payload)
        public_id: str = payload.get("sub")
        if public_id is None:
            print('public id is none')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="public_id is none"
            )
    except JWTError:
        print('jwt error')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT error"
        )
    user = user_crud_service.search_by_public_id(public_id)
    if user is None:
        print('user is none')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user is none"
        )
    return user
