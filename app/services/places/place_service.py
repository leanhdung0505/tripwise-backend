from fastapi import HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional, Tuple, Dict, Any
from app.models import (
    Message, Places, PlaceCreate, PlaceUpdate, PlacePublic,
    PlacePhotos, PlacePhotoCreate, PlacePhotoPublic,
    PaginationMetadata, PaginatedResponse
)
from app.crud.places.crud_place import crud_place

class PlaceService:
    def get_place(self, session: Session, place_id: int) -> PlacePublic:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        return place
    
    def get_places(self, session: Session, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Get one more item than the requested limit to check if there's a next page
        places = crud_place.get_multi(session=session, skip=skip, limit=limit + 1)
        
        # Check if there are more items
        has_next = len(places) > limit
        if has_next:
            places = places[:limit]  # Remove the extra item
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": places,
            "pagination": pagination
        }
    
    def get_places_by_city(self, session: Session, city: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Get one more item than the requested limit
        places = crud_place.get_by_city(session=session, city=city, skip=skip, limit=limit + 1)
        
        # Check if there are more items
        has_next = len(places) > limit
        if has_next:
            places = places[:limit]  # Remove the extra item
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": places,
            "pagination": pagination
        }
    
    def get_places_by_type(self, session: Session, type: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Get one more item than the requested limit
        places = crud_place.get_by_type(session=session, type=type, skip=skip, limit=limit + 1)
        
        # Check if there are more items
        has_next = len(places) > limit
        if has_next:
            places = places[:limit]  # Remove the extra item
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": places,
            "pagination": pagination
        }
    
    def get_places_by_city_and_type(self, session: Session, city: str, type: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Get one more item than the requested limit
        places = crud_place.get_by_city_and_type(session=session, city=city, type=type, skip=skip, limit=limit + 1)
        
        # Check if there are more items
        has_next = len(places) > limit
        if has_next:
            places = places[:limit]  # Remove the extra item
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": places,
            "pagination": pagination
        }
    
    def create_place(self, session: Session, place_in: PlaceCreate) -> PlacePublic:
        return crud_place.create(session=session, place_create=place_in)
    
    def update_place(self, session: Session, place_id: int, place_in: PlaceUpdate) -> PlacePublic:
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
        return Message(detail="Place deleted successfully")
    
    def add_photo(self, session: Session, place_id: int, photo_in: PlacePhotoCreate) -> PlacePhotoPublic:
        place = self.get_place(session=session, place_id=place_id)
        return crud_place.add_photo(session=session, place_id=place_id, photo_create=photo_in)
    
    def get_photos(self, session: Session, place_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        place = self.get_place(session=session, place_id=place_id)
        skip = (page - 1) * limit
        
        # Get all photos for now (we would ideally have a paginated version in crud_place)
        all_photos = crud_place.get_photos(session=session, place_id=place_id)
        
        # Do manual pagination since we have all photos
        total_photos = len(all_photos)
        start_idx = skip
        end_idx = min(skip + limit + 1, total_photos)
        
        photos = all_photos[start_idx:end_idx]
        
        # Check if there are more items
        has_next = end_idx < total_photos
        if len(photos) > limit:
            photos = photos[:limit]  # Remove the extra item if any
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": photos,
            "pagination": pagination
        }
    
    def delete_photo(self, session: Session, photo_id: int) -> Message:
        db_photo = session.get(PlacePhotos, photo_id)
        if not db_photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )
        crud_place.delete_photo(session=session, photo_id=photo_id)
        return Message(detail="Photo deleted successfully")

place_service = PlaceService()