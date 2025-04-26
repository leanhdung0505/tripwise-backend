from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional
from app.models import (
    RestaurantDetails, RestaurantDetailCreate, RestaurantDetailUpdate, 
    RestaurantDetailResponse, Message
)
from app.crud.places.crud_restaurant import crud_restaurant
from app.services.places.place_service import place_service

class RestaurantService:
    def get_restaurant_detail(self, session: Session, restaurant_detail_id: int) -> RestaurantDetails:
        restaurant_detail = crud_restaurant.get_by_id(session=session, restaurant_detail_id=restaurant_detail_id)
        if not restaurant_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant detail not found"
            )
        return restaurant_detail
    
    def get_restaurant_detail_by_place(self, session: Session, place_id: int) -> RestaurantDetails:
        # First check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        restaurant_detail = crud_restaurant.get_by_place_id(session=session, place_id=place_id)
        if not restaurant_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant detail not found for this place"
            )
        return restaurant_detail
    
    def get_restaurant_details(self, session: Session, skip: int = 0, limit: int = 100) -> List[RestaurantDetails]:
        return crud_restaurant.get_multi(session=session, skip=skip, limit=limit)
    
    def create_restaurant_detail(self, session: Session, place_id: int, restaurant_detail_in: RestaurantDetailCreate) -> RestaurantDetails:
        # Check if place exists and is a restaurant
        place = place_service.get_place(session=session, place_id=place_id)
        if place.type != "RESTAURANT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Place is not a restaurant"
            )
        
        # Check if restaurant detail already exists
        existing = crud_restaurant.get_by_place_id(session=session, place_id=place_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Restaurant detail already exists for this place"
            )
        
        return crud_restaurant.create(
            session=session, 
            place_id=place_id, 
            restaurant_detail_create=restaurant_detail_in
        )
    
    def update_restaurant_detail(self, session: Session, place_id: int, restaurant_detail_in: RestaurantDetailUpdate) -> RestaurantDetails:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing restaurant detail
        db_restaurant_detail = crud_restaurant.get_by_place_id(session=session, place_id=place_id)
        if not db_restaurant_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant detail not found for this place"
            )
        
        return crud_restaurant.update(
            session=session, 
            db_restaurant_detail=db_restaurant_detail, 
            restaurant_detail_in=restaurant_detail_in
        )
    
    def delete_restaurant_detail(self, session: Session, place_id: int) -> Message:
        # Check if place exists
        place = place_service.get_place(session=session, place_id=place_id)
        
        # Get existing restaurant detail
        db_restaurant_detail = crud_restaurant.get_by_place_id(session=session, place_id=place_id)
        if not db_restaurant_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant detail not found for this place"
            )
        
        crud_restaurant.delete_by_place_id(session=session, place_id=place_id)
        return Message(message="Restaurant detail deleted successfully")

restaurant_service = RestaurantService()