from fastapi import HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional, Tuple, Dict, Any
from app.models import (
    Message, Places, PlaceCreate, PlaceUpdate, PlacePublic,
    PlacePhotos, PlacePhotoCreate, PlacePhotoPublic,
    RestaurantDetails, HotelDetails, AttractionDetails,
    RestaurantDetailPublic, HotelDetailPublic, AttractionDetailPublic,
    PaginationMetadata, PaginatedResponse
)
from app.crud.places.crud_place import crud_place

class PlaceService:
    def _get_place_with_details(self, session: Session, place: Places) -> PlacePublic:
        """Helper method to get place with all details"""
        # Convert to dict to build PlacePublic
        place_data = place.dict()
        
        # Get photos
        photos = crud_place.get_photos(session=session, place_id=place.place_id)
        place_data["photos"] = photos
        
        # Get details based on place type
        place_data["restaurant_detail"] = None
        place_data["hotel_detail"] = None
        place_data["attraction_detail"] = None
        
        if place.type.upper() == "RESTAURANT":
            restaurant_detail = session.exec(
                select(RestaurantDetails).where(RestaurantDetails.place_id == place.place_id)
            ).first()
            if restaurant_detail:
                place_data["restaurant_detail"] = RestaurantDetailPublic(**restaurant_detail.dict())
        
        elif place.type.upper() == "HOTEL":
            hotel_detail = session.exec(
                select(HotelDetails).where(HotelDetails.place_id == place.place_id)
            ).first()
            if hotel_detail:
                place_data["hotel_detail"] = HotelDetailPublic(**hotel_detail.dict())
        
        elif place.type.upper() == "ATTRACTION":
            attraction_detail = session.exec(
                select(AttractionDetails).where(AttractionDetails.place_id == place.place_id)
            ).first()
            if attraction_detail:
                place_data["attraction_detail"] = AttractionDetailPublic(**attraction_detail.dict())
        
        return PlacePublic(**place_data)

    def get_place(self, session: Session, place_id: int) -> PlacePublic:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        return self._get_place_with_details(session=session, place=place)
    
    def get_places(self, session: Session, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit

        # Get one more item than the requested limit to check if there's a next page
        places = crud_place.get_multi(session=session, skip=skip, limit=limit + 1)
        total_items = crud_place.get_count(session=session)  
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(places) > limit
        if has_next:
            places = places[:limit]

        places_with_details = []
        for place in places:
            places_with_details.append(self._get_place_with_details(session=session, place=place))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": places_with_details,
            "pagination": pagination
        }
    
    def get_places_by_city(self, session: Session, city: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        places = crud_place.get_by_city(session=session, city=city, skip=skip, limit=limit + 1)
        total_items = crud_place.get_count_by_city(session=session, city=city)  
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(places) > limit
        if has_next:
            places = places[:limit]

        places_with_details = []
        for place in places:
            places_with_details.append(self._get_place_with_details(session=session, place=place))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": places_with_details,
            "pagination": pagination
        }
    
    def get_places_by_type(self, session: Session, type: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit

        places = crud_place.get_by_type(session=session, type=type, skip=skip, limit=limit + 1)
        total_items = crud_place.get_count_by_type(session=session, type=type)  # Bạn cần hàm này trong crud
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(places) > limit
        if has_next:
            places = places[:limit]

        places_with_details = []
        for place in places:
            places_with_details.append(self._get_place_with_details(session=session, place=place))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": places_with_details,
            "pagination": pagination
        }
    
    def get_places_by_city_and_type(self, session: Session, city: str, type: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit

        places = crud_place.get_by_city_and_type(session=session, city=city, type=type, skip=skip, limit=limit + 1)
        total_items = crud_place.get_count_by_city_and_type(session=session, city=city, type=type)  # Cần hàm này trong crud
        total_pages = (total_items + limit - 1) // limit if limit else 1

        has_next = len(places) > limit
        if has_next:
            places = places[:limit]

        places_with_details = []
        for place in places:
            places_with_details.append(self._get_place_with_details(session=session, place=place))

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
        )

        return {
            "data": places_with_details,
            "pagination": pagination
        }
    
    def create_place(self, session: Session, place_in: PlaceCreate) -> PlacePublic:
        place = crud_place.create(session=session, place_create=place_in)
        
        # Return place with empty details as it's a new place
        return self._get_place_with_details(session=session, place=place)
    
    def update_place(self, session: Session, place_id: int, place_in: PlaceUpdate) -> PlacePublic:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        updated_place = crud_place.update(session=session, db_place=place, place_in=place_in)
        
        return self._get_place_with_details(session=session, place=updated_place)
    
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
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        return crud_place.add_photo(session=session, place_id=place_id, photo_create=photo_in)
    
    def get_photos(self, session: Session, place_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        place = crud_place.get_by_id(session=session, place_id=place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )

        skip = (page - 1) * limit

        all_photos = crud_place.get_photos(session=session, place_id=place_id)
        total_photos = len(all_photos)
        total_pages = (total_photos + limit - 1) // limit if limit else 1

        start_idx = skip
        end_idx = min(skip + limit + 1, total_photos)
        photos = all_photos[start_idx:end_idx]

        has_next = end_idx < total_photos
        if len(photos) > limit:
            photos = photos[:limit]

        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next,
            total_pages=total_pages
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