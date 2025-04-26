from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from app.models import (
    Places, PlaceCreate, PlaceUpdate, PlaceResponse, 
    PlacePhotos, PlacePhotoCreate, PlacePhotoResponse, Message
)
from app.crud.places.crud_place import crud_place

class PlaceService:
    def get_place(self, session: Session, place_id: int) -> Places:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        return place
    
    def get_places(self, session: Session, skip: int = 0, limit: int = 100) -> List[Places]:
        return crud_place.get_multi(session=session, skip=skip, limit=limit)
    
    def get_places_by_city(self, session: Session, city: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return crud_place.get_by_city(session=session, city=city, skip=skip, limit=limit)
    
    def get_places_by_type(self, session: Session, type: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return crud_place.get_by_type(session=session, type=type, skip=skip, limit=limit)
    
    def get_places_by_city_and_type(self, session: Session, city: str, type: str, skip: int = 0, limit: int = 100) -> List[Places]:
        return crud_place.get_by_city_and_type(session=session, city=city, type=type, skip=skip, limit=limit)
    
    def create_place(self, session: Session, place_in: PlaceCreate) -> Places:
        return crud_place.create(session=session, place_create=place_in)
    
    def update_place(self, session: Session, place_id: int, place_in: PlaceUpdate) -> Places:
        db_place = self.get_place(session=session, place_id=place_id)
        return crud_place.update(session=session, db_place=db_place, place_in=place_in)
    
    def delete_place(self, session: Session, place_id: int) -> Message:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        crud_place.delete(session=session, place_id=place_id)
        return Message(message="Place deleted successfully")
    
    def add_photo(self, session: Session, place_id: int, photo_in: PlacePhotoCreate) -> PlacePhotos:
        place = self.get_place(session=session, place_id=place_id)
        return crud_place.add_photo(session=session, place_id=place_id, photo_create=photo_in)
    
    def get_photos(self, session: Session, place_id: int) -> List[PlacePhotos]:
        place = self.get_place(session=session, place_id=place_id)
        return crud_place.get_photos(session=session, place_id=place_id)
    
    def delete_photo(self, session: Session, photo_id: int) -> Message:
        db_photo = session.get(PlacePhotos, photo_id)
        if not db_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )
        crud_place.delete_photo(session=session, photo_id=photo_id)
        return Message(message="Photo deleted successfully")

place_service = PlaceService()