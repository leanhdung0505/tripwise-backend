from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import SessionDep, CurrentUser
from app.models import Token, UsersPublic
from app.services.auth.auth_service import auth_service

router = APIRouter(prefix="/login", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/", response_model=Token)
def login_access_token(
    session: SessionDep,
    login_data: LoginRequest
):
    return auth_service.login_access_token(
        session=session,
        email=login_data.email,
        password=login_data.password
    )

@router.post("/test-token", response_model=UsersPublic)
def test_token(current_user: CurrentUser):
    return current_user