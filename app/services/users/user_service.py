from fastapi import HTTPException, status
from sqlmodel import Session, select, func
from uuid import UUID
from app.crud.users.crud_user import crud_user
from app.models import Users, UserCreate, UserUpdate, UserUpdateMe, UsersPublic, Message

class UserService:
    def create_user(self, session: Session, user_in: UserCreate) -> Users:
        if crud_user.get_by_email(session=session, email=user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system"
            )
        return crud_user.create(session=session, user_create=user_in)

    def update_user(self, session: Session, current_user: Users, user_in: UserUpdateMe) -> Users:
        if user_in.email:
            existing_user = crud_user.get_by_email(session=session, email=user_in.email)
            if existing_user and existing_user.user_id != current_user.user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
        return crud_user.update(session=session, db_user=current_user, user_in=user_in)

    def update_user_admin(self, session: Session, user_id: UUID, user_in: UserUpdate) -> Users:
        db_user = session.get(Users, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return crud_user.update(session=session, db_user=db_user, user_in=user_in)

    # Thêm các phương thức mới cho admin
    def get_users(self, session: Session, skip: int = 0, limit: int = 100) -> UsersPublic:
        """Get list of all non-admin users with pagination"""
        # Query chỉ lấy non-admin users
        statement = select(Users).where(Users.role == 'user')
        
        # Đếm tổng số non-admin users
        count = session.exec(
            select(func.count()).select_from(Users).where(Users.role == 'user')
        ).one()
        
        # Lấy danh sách users với phân trang
        users = session.exec(
            statement.offset(skip).limit(limit)
        ).all()
        
        return UsersPublic(data=users, count=count)

    def get_user_by_id(self, session: Session, user_id: UUID) -> Users:
        """Get a specific user by ID"""
        user = session.get(Users, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def delete_user_admin(self, session: Session, current_user: Users, user_id: UUID) -> Message:
        """Delete a user (admin only)"""
        user = session.get(Users, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user == current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete yourself"
            )
        session.delete(user)
        session.commit()
        return Message(message="User deleted successfully")

    def delete_user_me(self, session: Session, current_user: Users) -> Message:
        """Delete own user account"""
        if current_user.role != 'user':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super users are not allowed to delete themselves"
            )
        session.delete(current_user)
        session.commit()
        return Message(message="User deleted successfully")

user_service = UserService()

