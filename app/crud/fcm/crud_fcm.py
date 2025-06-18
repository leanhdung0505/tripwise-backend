import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from app.models import FCMTokens, Users
from app.core.config import settings  # Assuming settings is imported from app.core.config

class CRUDFcm:
    def __init__(self):
        if not firebase_admin._apps:
            private_key = settings.PRIVATE_KEY_FIREBASE.replace('\\n', '\n')
            
            cred_dict = {
                "type": "service_account",
                "project_id": "trip-wise-fca39",
                "private_key_id": settings.PRIVATE_KEY_FIREBASE_ID,
                "private_key": private_key,
                "client_email": "firebase-adminsdk-fbsvc@trip-wise-fca39.iam.gserviceaccount.com",
                "client_id": "113382632026197703412",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40trip-wise-fca39.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

    def get_active_tokens(self, session: Session, user_id: str) -> List[FCMTokens]:
        """Get all active FCM tokens for a user"""
        return session.exec(
            select(FCMTokens)
            .where(FCMTokens.user_id == user_id)
            .where(FCMTokens.is_active == True)
        ).all()

    def create_or_update_token(self, session: Session, user_id: str, fcm_token: str, device: str) -> FCMTokens:
        """Create new FCM token or update existing one for a user"""
        # Kiểm tra xem token đã tồn tại chưa
        existing_token = session.exec(
            select(FCMTokens).where(
                (FCMTokens.user_id == user_id) &
                (FCMTokens.fcm_token == fcm_token)
            )
        ).first()
        
        if existing_token:
            # Nếu token đã tồn tại, cập nhật thành active và device info
            existing_token.is_active = True
            existing_token.device = device
            session.add(existing_token)
            session.commit()
            session.refresh(existing_token)
            return existing_token
        else:
            # Tạo token mới
            db_obj = FCMTokens(
                user_id=user_id,
                fcm_token=fcm_token,
                device=device,
                is_active=True
            )
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

    def create_token(self, session: Session, user_id: str, fcm_token: str, device: str) -> FCMTokens:
        """Create a new FCM token for a user (deprecated - use create_or_update_token)"""
        return self.create_or_update_token(session, user_id, fcm_token, device)

    def update_token_status(self, session: Session, token_id: int, is_active: bool) -> Optional[FCMTokens]:
        """Update FCM token status"""
        db_obj = session.get(FCMTokens, token_id)
        if db_obj:
            db_obj.is_active = is_active
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def deactivate_token_by_token(self, session: Session, user_id: str, fcm_token: str) -> Optional[FCMTokens]:
        """Deactivate FCM token by token string"""
        token_obj = session.exec(
            select(FCMTokens).where(
                (FCMTokens.user_id == user_id) &
                (FCMTokens.fcm_token == fcm_token)
            )
        ).first()
        
        if token_obj:
            token_obj.is_active = False
            session.add(token_obj)
            session.commit()
            session.refresh(token_obj)
        return token_obj

    def deactivate_all_user_tokens(self, session: Session, user_id: str) -> List[FCMTokens]:
        """Deactivate all FCM tokens for a user"""
        tokens = session.exec(
            select(FCMTokens).where(FCMTokens.user_id == user_id)
        ).all()
        
        updated_tokens = []
        for token in tokens:
            token.is_active = False
            session.add(token)
            updated_tokens.append(token)
        
        session.commit()
        return updated_tokens

    def activate_token_by_token(self, session: Session, user_id: str, fcm_token: str) -> Optional[FCMTokens]:
        """Activate FCM token by token string"""
        token_obj = session.exec(
            select(FCMTokens).where(
                (FCMTokens.user_id == user_id) &
                (FCMTokens.fcm_token == fcm_token)
            )
        ).first()
        
        if token_obj:
            token_obj.is_active = True
            session.add(token_obj)
            session.commit()
            session.refresh(token_obj)
        return token_obj

    def delete_token(self, session: Session, token_id: int) -> None:
        """Delete an FCM token"""
        db_obj = session.get(FCMTokens, token_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()

    def delete_token_by_token(self, session: Session, user_id: str, fcm_token: str) -> bool:
        """Delete FCM token by token string"""
        token_obj = session.exec(
            select(FCMTokens).where(
                (FCMTokens.user_id == user_id) &
                (FCMTokens.fcm_token == fcm_token)
            )
        ).first()
        
        if token_obj:
            session.delete(token_obj)
            session.commit()
            return True
        return False

    def send_notification(
        self,
        *,
        tokens: str | List[str],
        title: str,
        body: str,
        data: dict = None
    ) -> dict:
        """
        Gửi thông báo đến một hoặc nhiều token FCM
        """
        # Chuyển đổi token đơn lẻ thành list
        if isinstance(tokens, str):
            tokens = [tokens]

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
        )

        try:
            response = messaging.send_multicast(message)
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create and export an instance
crud_fcm = CRUDFcm()

# Make sure to export the instance
__all__ = ["crud_fcm"]