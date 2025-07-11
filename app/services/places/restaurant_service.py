from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional, Tuple
from app.models import (
    PaginationMetadata, RestaurantDetails, RestaurantDetailCreate, RestaurantDetailUpdate, 
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
    
    def get_restaurant_details(
        self, 
        session: Session, 
        page: int = 1, 
        limit: int = 10
    ) -> Tuple[List[RestaurantDetails], PaginationMetadata]:
        # Calculate skip value based on page and limit
        skip = (page - 1) * limit
        
        # Get total count
        total_count = crud_restaurant.get_count(session=session)
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if limit else 1
        
        # Get restaurant details for the current page
        restaurant_details = crud_restaurant.get_multi(session=session, skip=skip, limit=limit)
        
        # Create pagination metadata
        has_prev = page > 1
        has_next = (page * limit) < total_count
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=has_prev,
            has_next=has_next,
            total_pages=total_pages
        )
        
        return restaurant_details, pagination
    
    
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
        return Message(detail="Restaurant detail deleted successfully")

restaurant_service = RestaurantService()