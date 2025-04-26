# app/api/routes/user/admin.py

from fastapi import APIRouter, Depends
from uuid import UUID
from typing import Any

from app.api.deps import get_current_active_superuser, SessionDep, CurrentUser
from app.models import UserCreate, UserUpdate, UserPublic, UsersPublic, Message
from app.services.users.user_service import user_service

router = APIRouter(
    prefix="/admin",
    tags=["admin-users"],
    dependencies=[Depends(get_current_active_superuser)]
)

@router.get("/", response_model=UsersPublic)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get list of all users with pagination.
    """
    return user_service.get_users(session=session, skip=skip, limit=limit)

@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user by admin.
    """
    return user_service.create_user(session=session, user_in=user_in)

@router.patch("/{user_id}", response_model=UserPublic)
def update_user(*, session: SessionDep, user_id: UUID, user_in: UserUpdate) -> Any:
    """
    Update user information by admin.
    """
    return user_service.update_user_admin(session=session, user_id=user_id, user_in=user_in)

@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id_admin(user_id: UUID, session: SessionDep) -> Any:
    """
    Admin get any user by ID.
    """
    return user_service.get_user_by_id(session=session, user_id=user_id)

@router.delete("/{user_id}", response_model=Message)
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: UUID) -> Message:
    """
    Delete user by admin.
    """
    return user_service.delete_user_admin(
        session=session,
        current_user=current_user,
        user_id=user_id
    )
