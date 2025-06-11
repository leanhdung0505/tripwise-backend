# app/api/routes/user/users.py

from fastapi import APIRouter, Body, Depends, logger, UploadFile, File
from app.api.deps import CurrentUser, SessionDep
from app.models import ImageUploadPublic, ImageUploadResponse, Message, ChangePassword
from app.services.users.user_service import user_service
from app.services.auth.auth_service import auth_service
from app.services.cloudinary.cloudinary_service import upload_image_to_cloudinary
from app.repository.response.user_response import UserResponse, UserUpdateMe
from app.repository.request.user_request import UserUpdate
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: CurrentUser) -> UserResponse:
    """
    Get current user information.
    """
    return UserResponse(data=current_user)

@router.patch("/me", response_model=UserUpdateMe)
def update_user_me(
    *,
    session: SessionDep,
    user_in: UserUpdate = Body(...),
    current_user: CurrentUser
) -> UserUpdateMe:
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


@router.post("/me/avatar", response_model=ImageUploadResponse)
def upload_avatar(
    *,
    file: UploadFile = File(...)
) -> ImageUploadResponse :
    """
    Upload avatar to Cloudinary and update user's profile_picture.
    """
    # Upload lên Cloudinary
    image_url = upload_image_to_cloudinary(file.file)
    # Update user
    return ImageUploadResponse(data=ImageUploadPublic(image_url=image_url))

