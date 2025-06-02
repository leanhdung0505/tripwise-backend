import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import List, Dict, Any, Optional
from sqlmodel import Session
from app.crud.fcm.crud_fcm import crud_fcm

class FCMService:
    def __init__(self):
        # Chỉ khởi tạo 1 lần
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                os.path.join(os.path.dirname(""), os.getenv("FIREBASE_CREDENTIAL_PATH"))
            )
            firebase_admin.initialize_app(cred)

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

    def send_share_notification(self, session: Session, shared_with_user_id: str, owner_name: str, itinerary_id: str, permission: str) -> List[str]:
        """Send notification when an itinerary is shared"""
        # Get active tokens from crud
        tokens = crud_fcm.get_active_tokens(session, shared_with_user_id)
        fcm_tokens = [token.fcm_token for token in tokens]
        
        return self.send_notifications(
            tokens=fcm_tokens,
            title="Chia sẻ lịch trình mới",
            body=f"{owner_name} đã chia sẻ một lịch trình với bạn",
            data={
                "type": "itinerary_share",
                "itinerary_id": itinerary_id,
                "permission": permission
            }
        )

    def register_token_on_login(self, session: Session, user_id: str, fcm_token: str, device: str) -> object:
        """Register or reactivate FCM token when user logs in"""
        return crud_fcm.create_or_update_token(session, user_id, fcm_token, device)

    def register_token(self, session: Session, user_id: str, fcm_token: str, device: str):
        """Register a new FCM token for a user (deprecated - use register_token_on_login)"""
        return self.register_token_on_login(session, user_id, fcm_token, device)

    def deactivate_token_on_logout(self, session: Session, user_id: str, fcm_token: str) -> Optional[object]:
        """Deactivate FCM token when user logs out"""
        return crud_fcm.deactivate_token_by_token(session, user_id, fcm_token)

    def deactivate_all_user_tokens(self, session: Session, user_id: str) -> List[object]:
        """Deactivate all FCM tokens for a user (useful for logout from all devices)"""
        return crud_fcm.deactivate_all_user_tokens(session, user_id)

    def deactivate_token(self, session: Session, token_id: int):
        """Deactivate an FCM token by ID"""
        return crud_fcm.update_token_status(session, token_id, False)

    def remove_token(self, session: Session, user_id: str, fcm_token: str) -> bool:
        """Completely remove FCM token from database"""
        return crud_fcm.delete_token_by_token(session, user_id, fcm_token)

fcm_service = FCMService()

__all__ = ["fcm_service"]