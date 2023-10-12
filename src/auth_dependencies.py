from fastapi import HTTPException, Depends, status
from jose import jwt, JWTError
from src.database.services.crud import UserCRUDService, get_user_service
from src.database.models import User


async def get_authorised_user(token: str = None, user_crud_service: UserCRUDService = Depends(get_user_service)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, key='', options={'verify_signature': False})
        public_id: str = payload.get("sub")
        if public_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_crud_service.search_by_public_id(public_id)
    if user is None:
        raise credentials_exception
    return user
