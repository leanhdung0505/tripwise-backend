import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import List, Dict, Any, Optional
from sqlmodel import Session
from app.crud.fcm.crud_fcm import crud_fcm
from app.core.config import settings

class FCMService:
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

    def send_share_notification(self, session: Session, shared_with_user_id: str, owner_name: str, itinerary_id: str, permission: str) -> List[str]:
        """Send notification when an itinerary is shared"""
        # Get active tokens from crud
        tokens_objs = crud_fcm.get_active_tokens(session, shared_with_user_id)
        tokens: List[str] = [t.fcm_token for t in tokens_objs if t.is_active]
        return self.send_notification(
            tokens=tokens,
            title="Share new itinerary",
            body=f"{owner_name} shared a new itinerary with you",
            data={
                "type": "itinerary_share",
                "itinerary_id": itinerary_id,
                "permission": permission
            }
        )
    def send_notification(self, tokens: str | List[str], title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        try:
            results = []
            # Nếu là list, gửi từng token một
            if isinstance(tokens, list):
                for token in tokens:
                    if not token:
                        continue
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data=data,
                        token=token
                    )
                    response = messaging.send(message)
                    results.append({"token": token, "message_id": response})
                return {"success": True, "results": results}
            # Nếu là string, gửi một token
            elif isinstance(tokens, str) and tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body
                    ),
                    data=data,
                    token=tokens
                )
                response = messaging.send(message)
                return {"success": True, "message_id": response}
            else:
                return {"success": False, "error": "No valid token(s) provided"}
        except Exception as e:
            print(f"Error sending notification: {e}")
            return {"success": False, "error": str(e)}
    def register_token_on_login(self, session: Session, user_id: str, fcm_token: str, device: str) -> object:
        """Register orreactivate FCM token when user logs in"""
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