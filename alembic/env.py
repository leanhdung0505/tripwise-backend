import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object, lấy từ file alembic.ini
config = context.config

# Setup logging
fileConfig(config.config_file_name)

# Load settings từ app config
from app.core.config import settings  # noqa

# Import tất cả model để Alembic biết schema
from app.models import (
    SQLModel,
    Places,
    Users,
    PlacePhotos,
    RestaurantDetails,
    HotelDetails,
    AttractionDetails,
    Itineraries,
    ItineraryDays,
    ItineraryActivities,
    
)  # noqa

# Gán metadata để Alembic autogenerate migration script
target_metadata = SQLModel.metadata

def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline():
    """Chạy migration ở chế độ offline (không cần kết nối DB)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Chạy migration ở chế độ online (có kết nối DB)."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
