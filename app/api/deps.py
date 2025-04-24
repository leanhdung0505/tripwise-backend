from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from app.core.security import ALGORITHM
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, Users, Token

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep,
    token: str = Depends(reusable_oauth2),
) -> Users:  
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(Users, token_data.sub)  
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[Users, Depends(get_current_user)]  


# def get_current_active_user(
#     current_user: CurrentUser,
# ) -> Users:  
#     if not current_user:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


def get_current_active_superuser(
    current_user: CurrentUser,
) -> Users:  
    if current_user.role == 'user':
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

