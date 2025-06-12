import httpx
from datetime import timedelta
from fastapi import HTTPException, status
from sqlmodel import Session
from google.auth.transport import requests
from google.oauth2 import id_token
from typing import Optional

from app.crud.users.crud_user import crud_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models import Users
from app.repository.request.user_request import UserCreate
from app.models import GoogleUserInfo
from app.repository.response.login_response import Token
from app.services.fcm.fcm_service import fcm_service

class GoogleAuthService:
    @staticmethod
    async def verify_google_token(token: str) -> GoogleUserInfo:
        """Verify Google ID token and get user info"""
        try:
            # Method 1: Using Google's tokeninfo endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google token"
                    )
                
                user_data = response.json()
                return GoogleUserInfo(**user_data)
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to verify Google token: {str(e)}"
            )
    
    @staticmethod
    async def google_login(
        session: Session, 
        google_token: str, 
        fcm_token: Optional[str] = None, 
        device: Optional[str] = None
    ) -> Token:
        """Login or register user with Google OAuth"""
        # Verify token and get user info from Google
        google_user = await GoogleAuthService.verify_google_token(google_token)
        
        if not google_user.verified_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google email is not verified"
            )
        
        # Check if user already exists
        existing_user = crud_user.get_by_email(session=session, email=google_user.email)
        
        if existing_user:
            # User exists, check if active
            if not existing_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            # User exists and active, login directly
            user = existing_user
        else:
            # Create new user with Google info
            user_create = UserCreate(
                username=google_user.email.split('@')[0],  # Use email prefix as username
                email=google_user.email,
                full_name=google_user.name,
                profile_picture=google_user.picture,
                password="google_oauth_user",  # Placeholder password for OAuth users
                role="user",  # Default role
                is_active=True  # New users are active by default
            )
            
            # Check if username already exists, if so, append numbers
            base_username = user_create.username
            counter = 1
            while crud_user.get_by_username(session=session, username=user_create.username):
                user_create.username = f"{base_username}{counter}"
                counter += 1
            
            try:
                user = crud_user.create(session=session, user_create=user_create)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(e)}"
                )
        
        # Xử lý FCM token khi login Google (tương tự như login thường)
        if fcm_token and device:
            fcm_service.register_token_on_login(session, user.user_id, fcm_token, device)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.user_id)
        refresh_token = create_refresh_token(user.user_id)
        
        return Token(access_token=access_token, refresh_token=refresh_token)

google_auth_service = GoogleAuthService()