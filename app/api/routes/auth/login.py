from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import SessionDep, CurrentUser
from app.models import ResponseWrapper
from app.repository.request.login_request import LoginRequest
from app.services.auth.auth_service import auth_service
from app.repository.response.user_response import UserResponse
from app.repository.response.login_response import LoginResponse, Token
router = APIRouter(prefix="/login", tags=["auth"])

@router.post("/", response_model=LoginResponse)
def login_access_token(
    session: SessionDep,
    login_data: LoginRequest
):
    return LoginResponse(
        data=auth_service.login_access_token(
            session=session,
            email=login_data.email,
            password=login_data.password,
            device=login_data.device,
            fcm_token=login_data.fcm_token
        )
    )
@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: CurrentUser):
    return current_user