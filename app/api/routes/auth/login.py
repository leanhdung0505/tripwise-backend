from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import SessionDep, CurrentUser
from app.models import Token, UsersPublic
from app.services.auth.auth_service import auth_service

router = APIRouter(prefix="/login", tags=["auth"])

@router.post("/access-token", response_model=Token)
def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    return auth_service.login_access_token(
        session=session,
        email=form_data.username,
        password=form_data.password
    )

@router.post("/test-token", response_model=UsersPublic)
def test_token(current_user: CurrentUser):
    return current_user
