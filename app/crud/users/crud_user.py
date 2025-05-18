from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.models import Users
from app.repository.request.user_request import UserCreate, UserUpdate
class CRUDUser:
    def get_by_email(self, session: Session, email: str) -> Optional[Users]:
        return session.exec(select(Users).where(Users.email == email)).first()
    
    def get_by_username(self, session: Session, username: str) -> Users | None:
        statement = select(Users).where(Users.username == username)
        return session.exec(statement).first()
    
    def create(self, session: Session, user_create: UserCreate) -> Users:
        db_obj = Users(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            password=get_password_hash(user_create.password),
            role=user_create.role,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(self, session: Session, db_user: Users, user_in: UserUpdate) -> Users:
        update_data = user_in.model_dump(exclude_unset=True)
        db_user.updated_at = datetime.now()
        db_user.sqlmodel_update(update_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    def authenticate(self, session: Session, email: str, password: str) -> Optional[Users]:
        user = self.get_by_email(session=session, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def update_password(self, session: Session, user: Users, new_password: str) -> Users:
        user.password = get_password_hash(new_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# Create and export an instance
crud_user = CRUDUser()

# Make sure to export the instance
__all__ = ["crud_user"]
