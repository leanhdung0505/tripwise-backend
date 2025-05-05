# app/api/routes/auth/password.py

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import SessionDep, CurrentUser
from app.core.security import get_password_hash, verify_password
from app.crud.users.crud_user import crud_user
from app.models import NewPassword, Message, ChangePassword

router = APIRouter(prefix="/password", tags=["auth"])

@router.post("/change", response_model=Message)
def change_password(
    session: SessionDep,
    current_user: CurrentUser,  # Requires authentication
    data: ChangePassword
):
    """
    Change password for logged in user.
    Requires authentication.
    """
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    current_user.password = get_password_hash(data.new_password)
    session.add(current_user)
    session.commit()
    return Message(detail="Password changed successfully")


@router.post("/reset-by-email", response_model=Message)
def reset_password(
    session: SessionDep,  # No authentication required
    body: NewPassword
):
    """
    Reset password after email verification through OTP.
    No authentication required - verification was done through OTP.
    """
    user = crud_user.get_by_email(session=session, email=body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.password = get_password_hash(body.new_password)
    session.add(user)
    session.commit()
    return Message(detail="Password reset successfully")
