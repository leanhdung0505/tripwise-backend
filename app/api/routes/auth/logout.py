from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel import Session
from app.api.deps import SessionDep, CurrentUser
from app.models import FCMTokens, Message
from app.services.fcm.fcm_service import fcm_service
from app.services.auth import auth_service
router = APIRouter(prefix="/logout", tags=["auth"])

@router.post("")
def logout_user(
    current_user: CurrentUser,
    session: SessionDep,
    
) -> Message:
    """
    Logout user and deactivate FCM token
    """
    return auth_service.logout_user(
        session=session,
        user_id=current_user.user_id,
        fcm_token=FCMTokens.fcm_token
    )

@router.post("/all", response_model=Message)
def logout_from_all_devices(
    current_user: CurrentUser,
    session: SessionDep
) -> Message:
    """
    Logout user from all devices by deactivating all FCM tokens
    """
    return auth_service.logout_from_all_devices(
        session=session,
        user_id=current_user.user_id
    )
