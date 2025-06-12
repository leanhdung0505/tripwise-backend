from datetime import timedelta
from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud.users.crud_user import crud_user
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password, verify_token
from app.models import Message, ChangePassword, NewPassword
from app.repository.response.login_response import Token
from app.services.fcm.fcm_service import fcm_service

class AuthService:
    @staticmethod
    def login_access_token(session: Session, email: str, password: str, fcm_token: str = None, device: str = None) -> Token:
        user = crud_user.authenticate(session=session, email=email, password=password)
        if not user:
            raise HTTPException(
                status_code=400, 
                detail="Incorrect email or password"
            )

        if fcm_token and device:
            fcm_service.register_token_on_login(session, user.user_id, fcm_token, device)
        access_token = create_access_token(user.user_id)
        refresh_token = create_refresh_token(user.user_id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def change_password(
        session: Session,
        current_user,
        data: ChangePassword
    ) -> Message:
        """Change password for logged in user"""
        if not verify_password(data.old_password, current_user.password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect current password"
            )

        if data.old_password == data.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password must be different from current password"
            )

        current_user.password = get_password_hash(data.new_password)
        session.add(current_user)
        session.commit()
        return Message(detail="Password changed successfully")

    @staticmethod
    def reset_password_by_email(
        session: Session,
        body: NewPassword
    ) -> Message:
        """Reset password after email verification through OTP"""
        user = crud_user.get_by_email(session=session, email=body.email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.password = get_password_hash(body.new_password)
        session.add(user)
        session.commit()
        return Message(detail="Password reset successfully")
    @staticmethod
    def logout_user(session: Session, user_id: str, fcm_token: str = None) -> Message:
        """Logout user and deactivate FCM token"""
        if fcm_token:
            # Deactivate specific token
            fcm_service.deactivate_token_on_logout(session, user_id, fcm_token)
        else:
            # Deactivate all tokens if no specific token provided
            fcm_service.deactivate_all_user_tokens(session, user_id)
        
        return Message(detail="Logged out successfully")

    @staticmethod
    def logout_from_all_devices(session: Session, user_id: str) -> Message:
        """Logout user from all devices by deactivating all FCM tokens"""
        fcm_service.deactivate_all_user_tokens(session, user_id)
        return Message(detail="Logged out from all devices successfully")
    
    @staticmethod
    def refresh_token(session: Session, refresh_token: str) -> Token:
        payload = verify_token(refresh_token)
        if payload.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        user = crud_user.get_by_id(session=session, user_id=payload.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        access_token = create_access_token(user.user_id)
        new_refresh_token = create_refresh_token(user.user_id)
        return Token(access_token=access_token, refresh_token=new_refresh_token)
    
auth_service = AuthService()
