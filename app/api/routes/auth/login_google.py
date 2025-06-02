# app/api/routes/google_auth.py
from fastapi import APIRouter, Depends
from app.api.deps import SessionDep
from app.models import GoogleLoginRequest
from app.repository.response.login_response import LoginResponse
from app.services.auth.google.google_auth_service import google_auth_service

router = APIRouter(prefix="/google", tags=["google-auth"])

@router.post("/login", response_model=LoginResponse)
async def google_login(
    session: SessionDep,
    google_data: GoogleLoginRequest
):
    """
    Login with Google OAuth
    
    Steps:
    1. Frontend sends Google access token
    2. Verify token with Google API
    3. Check if user exists by email
    4. If exists: login directly
    5. If not exists: create new user and login
    """
    token = await google_auth_service.google_login(
        session=session,
        google_token=google_data.token,
        fcm_token=google_data.fcm_token,
        device=google_data.device
    )
    
    return LoginResponse(data=token)