from typing import Annotated, Generator, Optional
import jwt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from app.core.security import ALGORITHM
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import  Users
from app.repository.response.login_response import TokenPayload, Token

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(
    session: SessionDep,
    authorization: Optional[str] = Security(api_key_header),
) -> Users:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remove 'Bearer ' prefix if present
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError, InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = session.get(Users, token_data.sub)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

CurrentUser = Annotated[Users, Depends(get_current_user)]

def get_current_active_superuser(
    current_user: CurrentUser,
) -> Users:
    if current_user.role == 'user':
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user