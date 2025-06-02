import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from app.models import FCMTokens

class CRUDFcm:
    def __init__(self):
        # Chỉ khởi tạo 1 lần
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                os.path.join(os.path.dirname(""), os.getenv("FIREBASE_CREDENTIAL_PATH"))
            )
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

    def send_notification(self, token: str, title: str, body: str, data: Dict[str, Any] = None) -> str:
        """Send FCM notification to a single token"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            data=data or {}
        )
        return messaging.send(message)

    def send_notifications(self, tokens: List[str], title: str, body: str, data: Dict[str, Any] = None) -> List[str]:
        """Send FCM notification to multiple tokens"""
        if not tokens:
            return []

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            tokens=tokens,
            data=data or {}
        )
        response = messaging.send_multicast(message)
        return [result.message_id for result in response.responses if result.success]

    def send_share_notification(self, tokens: List[str], owner_name: str, itinerary_id: str, permission: str) -> List[str]:
        """Send notification when an itinerary is shared"""
        return self.send_notifications(
            tokens=tokens,
            title="Share new itinerary",
            body=f"{owner_name} shared a new itinerary with you",
            data={
                "type": "itinerary_share",
                "itinerary_id": itinerary_id,
                "permission": permission
            }
        )

# Create and export an instance
crud_fcm = CRUDFcm()

# Make sure to export the instance
__all__ = ["crud_fcm"]