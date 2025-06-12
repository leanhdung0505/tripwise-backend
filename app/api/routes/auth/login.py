from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session
from datetime import timedelta
from app.api.deps import SessionDep, CurrentUser, get_current_user, get_session
from app.crud.fcm.crud_fcm import crud_fcm
from app.crud.users.crud_user import crud_user
from app.models import Message, ResponseWrapper, Users
from app.repository.request.login_request import LoginRequest
from app.services.auth.auth_service import auth_service
from app.repository.response.user_response import UserResponse
from app.repository.response.login_response import LoginResponse, Token
from app.services.fcm.fcm_service import fcm_service
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

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

@router.post("/admin", response_model=LoginResponse)
def admin_login_access_token(
    session: SessionDep,
    login_data: LoginRequest
):
    user = crud_user.authenticate(session=session, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin role required."
        )

    access_token = create_access_token(user.user_id)
    refresh_token = create_refresh_token(user.user_id)
    return LoginResponse(data=Token(access_token=access_token, refresh_token=refresh_token))

@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: CurrentUser):
    return current_user

@router.post("/send-test", response_model=Message)
async def send_test_notification(
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user)
):
    """
    Gửi thông báo test đến tất cả thiết bị của người dùng hiện tại.
    """
    try:
        
        # Sử dụng fcm_token_service để lấy tokens
        tokens = crud_fcm.get_active_tokens(
            session=session, 
            user_id=current_user.user_id
        )
        print(f"Tokens for user {current_user.user_id}: {tokens}")
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No FCM tokens registered for this user"
            )
        
        print(f"{tokens[0].fcm_token}")
        # Gửi thông báo đến token đầu tiên
        result = fcm_service.send_notification(
            tokens=tokens[0].fcm_token,
            title="Thông báo test",
            body="Đây là thông báo test từ VietFood Lens",
            data={"type": "test"}
        )
        
        print(f"FCM send result: {result}")
        if result.get("success"):
            return Message(detail="Test notification sent successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to send test notification")
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/send-test", response_model=Message)
async def send_test_notification(
    session: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user)
):
    """
    Gửi thông báo test đến tất cả thiết bị của người dùng hiện tại.
    """
    try:
        
        # Sử dụng fcm_token_service để lấy tokens
        tokens = crud_fcm.get_active_tokens(
            session=session, 
            user_id=current_user.user_id
        )
        print(f"Tokens for user {current_user.user_id}: {tokens}")
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No FCM tokens registered for this user"
            )
        
        print(f"{tokens[0].fcm_token}")
        # Gửi thông báo đến token đầu tiên
        result = fcm_service.send_notification(
            tokens=tokens[0].fcm_token,
            title="Thông báo test",
            body="Đây là thông báo test từ VietFood Lens",
            data={"type": "test"}
        )
        
        print(f"FCM send result: {result}")
        if result.get("success"):
            return Message(detail="Test notification sent successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to send test notification")
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=LoginResponse)
def refresh_access_token(
    session: SessionDep,
    data: RefreshRequest
):
    token = auth_service.refresh_token(session=session, refresh_token=data.refresh_token)
    return LoginResponse(data=token)