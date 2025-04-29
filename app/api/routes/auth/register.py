from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser, SessionDep
from app.services.users.user_service import user_service
from app.repository.request.user_request import UserCreate
from app.repository.response.user_response import UserResponse
router = APIRouter(prefix="/register", tags=["auth"])

@router.post(
    "/", 
    response_model=UserResponse,
    responses={
        400: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
def register_user(
    session: SessionDep,
    # current_user: CurrentUser,
    user_in: UserCreate
):
    """
    Register a new user.
    
    Creates a new user account with the provided email, password and user information.
    Returns the created user without sensitive data.
    """
    return UserResponse(data= user_service.create_user(session=session, user_in=user_in))
