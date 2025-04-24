from sqlalchemy.pool import NullPool
from sqlmodel import Session, create_engine, select
import logging

from app import crud
from app.core.config import settings
from app.models import Users, UserCreate

logger = logging.getLogger(__name__)

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DB_ECHO,
    poolclass=NullPool,
)

def init_db(session: Session) -> None:
    # Check if superuser exists
    user = session.exec(
        select(Users).where(Users.email == settings.FIRST_SUPERUSER)
    ).first()
    
    if not user:
        # Create superuser if not exists
        username = settings.FIRST_SUPERUSER.split('@')[0]
        user_in = UserCreate(
            username=username,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="System Administrator",
        )
        logger.info(f"Creating user with data: {user_in.model_dump()}")
        crud.create_user(session=session, user_create=user_in)
