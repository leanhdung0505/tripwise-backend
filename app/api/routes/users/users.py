# app/api/routes/user/users.py

from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser, SessionDep
from app.models import UserPublic, UserUpdateMe, Message, ChangePassword
from app.services.users.user_service import user_service
from app.services.auth.auth_service import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> UserPublic:
    """
    Get current user information.
    """
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser
) -> UserPublic:
    """
    Update current user information.
    """
    return user_service.update_user(
        session=session,
        current_user=current_user,
        user_in=user_in
    )


@router.patch("/me/password", response_model=Message)
def change_password_me(
    *,
    session: SessionDep,
    password_in: ChangePassword,
    current_user: CurrentUser
) -> Message:
    """
    Change current user's password.
    """
    return auth_service.change_password(
        session=session,
        current_user=current_user,
        data=password_in
    )


@router.delete("/me", response_model=Message)
def delete_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUser
) -> Message:
    """
    Delete current user account.
    """
    return user_service.delete_user_me(
        session=session,
        current_user=current_user
    )


