from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import func
from app.models import Places, PlaceCreate, PlaceUpdate, PlacePhotos, PlacePhotoCreate

class CRUDPlace:
    def get_by_id(self, session: Session, place_id: int) -> Optional[Places]:
        return session.get(Places, place_id)
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[Places]:
        return session.exec(select(Places).offset(skip).limit(limit)).all()
    
    def get_by_city(self, session: Session, city: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return session.exec(select(Places).where(Places.city == city).offset(skip).limit(limit)).all()
    
    def get_by_type(self, session: Session, type: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return session.exec(select(Places).where(Places.type == type).offset(skip).limit(limit)).all()
    
    def get_by_city_and_type(self, session: Session, city: str, type: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return session.exec(
            select(Places).where(Places.city == city, Places.type == type).offset(skip).limit(limit)
        ).all()
    
    def create(self, session: Session, place_create: PlaceCreate) -> Places:
        db_obj = Places(
            name=place_create.name,
            local_name=place_create.local_name,
            description=place_create.description,
            type=place_create.type,
            address=place_create.address,
            city=place_create.city,
            latitude=place_create.latitude,
            longitude=place_create.longitude,
            rating=place_create.rating,
            price_range=place_create.price_range,
            phone=place_create.phone,
            email=place_create.email,
            website=place_create.website,
            web_url=place_create.web_url,
            image=place_create.image,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, db_place: Places, place_in: PlaceUpdate) -> Places:
        update_data = place_in.model_dump(exclude_unset=True)
        db_place.sqlmodel_update(update_data)
        session.add(db_place)
        session.commit()
        session.refresh(db_place)
        return db_place
    
    def delete(self, session: Session, place_id: int) -> None:
        db_obj = session.get(Places, place_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def add_photo(self, session: Session, place_id: int, photo_create: PlacePhotoCreate) -> PlacePhotos:
        db_obj = PlacePhotos(
            place_id=place_id,
            photo_url=photo_create.photo_url,
            is_primary=photo_create.is_primary
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def get_photos(self, session: Session, place_id: int) -> List[PlacePhotos]:
        return session.exec(select(PlacePhotos).where(PlacePhotos.place_id == place_id)).all()
    
    def delete_photo(self, session: Session, photo_id: int) -> None:
        db_obj = session.get(PlacePhotos, photo_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    def get_count(self, session: Session) -> int:
            result = session.exec(select(func.count()).select_from(Places))
            return result.one()
    def get_count_by_city(self, session: Session, city: str) -> int:
        result = session.exec(select(func.count()).select_from(Places).where(Places.city == city))
        return result.one()
    def get_count_by_type(self, session: Session, type: str) -> int:
        result = session.exec(select(func.count()).select_from(Places).where(Places.type == type))
        return result.one()
    def get_count_by_city_and_type(self, session: Session, city: str, type: str) -> int:
        result = session.exec(
            select(func.count()).select_from(Places).where(Places.city == city, Places.type == type)
        )
        return result.one()
# Create and export an instance
crud_place = CRUDPlace()

# Make sure to export the instance
__all__ = ["crud_place"]