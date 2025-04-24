from fastapi import APIRouter, HTTPException
from app.api.deps import SessionDep
from app.models import UserPublic, UserRegister
from app.services.users.user_service import user_service

router = APIRouter(prefix="/register", tags=["auth"])

@router.post(
    "/", 
    response_model=UserPublic,
    responses={
        400: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
def register_user(
    session: SessionDep,
    user_in: UserRegister
):
    """
    Register a new user.
    
    Creates a new user account with the provided email, password and user information.
    Returns the created user without sensitive data.
    """
    return user_service.create_user(session=session, user_in=user_in)
