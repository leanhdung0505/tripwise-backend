from fastapi import HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.models import (
    Message, Itineraries, ItineraryCreate, ItineraryUpdate, ItineraryPublic,
    ItineraryDays, ItineraryDayCreate, ItineraryDayUpdate, ItineraryDayPublic,
    ItineraryActivities, ItineraryActivityCreate, ItineraryActivityUpdate, ItineraryActivityPublic,
    PaginationMetadata, PaginatedResponse
)
from app.crud.itineraries.crud_itinerary import crud_itinerary
from app.services.places.place_service import place_service
from datetime import date

class ItineraryService:
    def get_itinerary(self, session: Session, itinerary_id: int) -> ItineraryPublic:
        itinerary = crud_itinerary.get_by_id(session=session, itinerary_id=itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )

        # Fetch days for this itinerary
        days = crud_itinerary.get_days(session=session, itinerary_id=itinerary_id)
        days_with_data = []

        for day in days:
            day_data = day.dict()
            # KHÔNG xử lý hotel ở đây nữa

            # Add activities for this day
            activities = crud_itinerary.get_activities(session=session, day_id=day.day_id)
            activities_with_place = []

            for activity in activities:
                activity_data = activity.dict()
                place = place_service.get_place(session=session, place_id=activity.place_id)
                activity_data["place"] = place
                activities_with_place.append(ItineraryActivityPublic(**activity_data))

            day_data["activities"] = activities_with_place
            days_with_data.append(ItineraryDayPublic(**day_data))

        # Create ItineraryPublic with days included
        itinerary_data = itinerary.dict()
        itinerary_data["days"] = days_with_data

        # Lấy hotel nếu có
        itinerary_data["hotel"] = None
        if itinerary.hotel_id:
            itinerary_data["hotel"] = place_service.get_place(session=session, place_id=itinerary.hotel_id)

        return ItineraryPublic(**itinerary_data)
    
    def get_itineraries(self, session: Session, user_id: UUID = None, destination: str = None, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        skip = (page - 1) * limit
        
        # Get itineraries based on filters
        if user_id:
            itineraries = crud_itinerary.get_by_user_id(session=session, user_id=str(user_id), skip=skip, limit=limit + 1)
        elif destination:
            itineraries = crud_itinerary.get_by_destination(session=session, destination=destination, skip=skip, limit=limit + 1)
        else:
            itineraries = crud_itinerary.get_multi(session=session, skip=skip, limit=limit + 1)
        
        # Check if there are more items
        has_next = len(itineraries) > limit
        if has_next:
            itineraries = itineraries[:limit]  # Remove the extra item
        
        itineraries_with_data = []
        for itinerary in itineraries:
            # We just include the basic itinerary data without days to keep response size manageable
            # Days can be fetched separately when needed
            itineraries_with_data.append(ItineraryPublic(**itinerary.dict()))
        
        pagination = PaginationMetadata(
            page=page,
            limit=limit,
            has_prev=page > 1,
            has_next=has_next
        )
        
        return {
            "data": itineraries_with_data,
            "pagination": pagination
        }
    
    def create_itinerary(self, session: Session, user_id: UUID, itinerary_in: ItineraryCreate) -> ItineraryPublic:
        # Validate dates
        if itinerary_in.start_date > itinerary_in.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after end date"
            )
        
        itinerary = crud_itinerary.create(session=session, itinerary_create=itinerary_in, user_id=str(user_id))
        
        # Add empty days list as it's a new itinerary
        itinerary_data = itinerary.dict()
        itinerary_data["days"] = []
        
        return ItineraryPublic(**itinerary_data)
    
    def update_itinerary(self, session: Session, user_id: UUID, itinerary_id: int, itinerary_in: ItineraryUpdate) -> ItineraryPublic:
        # Get the itinerary and verify ownership
        itinerary = self._get_user_itinerary(session, user_id, itinerary_id)
        
        # Validate dates if provided
        if itinerary_in.start_date and itinerary_in.end_date and itinerary_in.start_date > itinerary_in.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after end date"
            )
        elif itinerary_in.start_date and not itinerary_in.end_date and itinerary_in.start_date > itinerary.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date cannot be after current end date"
            )
        elif itinerary_in.end_date and not itinerary_in.start_date and itinerary_in.end_date < itinerary.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date cannot be before current start date"
            )
        
        updated_itinerary = crud_itinerary.update(session=session, db_itinerary=itinerary, itinerary_in=itinerary_in)
        
        # Return the updated itinerary with all details
        return self.get_itinerary(session=session, itinerary_id=itinerary_id)
    
    def delete_itinerary(self, session: Session, user_id: UUID, itinerary_id: int) -> Message:
        # Get the itinerary and verify ownership
        itinerary = self._get_user_itinerary(session, user_id, itinerary_id)
        
        crud_itinerary.delete(session=session, itinerary_id=itinerary_id)
        return Message(detail="Itinerary deleted successfully")
    
    def add_day(self, session: Session, user_id: UUID, itinerary_id: int, day_in: ItineraryDayCreate) -> ItineraryDayPublic:
        # Get the itinerary and verify ownership
        itinerary = self._get_user_itinerary(session, user_id, itinerary_id)
        
        # Validate day date is within itinerary date range
        if day_in.date < itinerary.start_date or day_in.date > itinerary.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Day date must be within itinerary date range"
            )
        
        day = crud_itinerary.create_day(session=session, itinerary_id=itinerary_id, day_create=day_in)
        
        # Add empty activities list as it's a new day
        day_data = day.dict()
        day_data["activities"] = []
        
        return ItineraryDayPublic(**day_data)
    
    def update_day(self, session: Session, user_id: UUID, day_id: int, day_in: ItineraryDayUpdate) -> ItineraryDayPublic:
        # Get the day
        day = crud_itinerary.get_day_by_id(session=session, day_id=day_id)
        if not day:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Day not found"
            )
        
        # Get the itinerary and verify ownership
        itinerary = self._get_user_itinerary(session, user_id, day.itinerary_id)
        
        # Validate date is within itinerary range if provided
        if day_in.date:
            if day_in.date < itinerary.start_date or day_in.date > itinerary.end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Day date must be within itinerary date range"
                )
        
        # Verify hotel exists if provided
        if day_in.hotel_id:
            place_service.get_place(session=session, place_id=day_in.hotel_id)
        
        updated_day = crud_itinerary.update_day(session=session, db_day=day, day_in=day_in)
        
        # Fetch activities for this day
        activities = crud_itinerary.get_activities(session=session, day_id=day_id)
        activities_with_place = []
        
        for activity in activities:
            activity_data = activity.dict()
            place = place_service.get_place(session=session, place_id=activity.place_id)
            activity_data["place"] = place
            activities_with_place.append(ItineraryActivityPublic(**activity_data))
        
        # Create ItineraryDayPublic with activities included
        day_data = updated_day.dict()
        day_data["activities"] = activities_with_place
        
        # Add hotel data if present
        if updated_day.hotel_id:
            hotel = place_service.get_place(session=session, place_id=updated_day.hotel_id)
            day_data["hotel"] = hotel
        
        return ItineraryDayPublic(**day_data)
    
    def delete_day(self, session: Session, user_id: UUID, day_id: int) -> Message:
        # Get the day
        day = crud_itinerary.get_day_by_id(session=session, day_id=day_id)
        if not day:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Day not found"
            )
        
        # Get the itinerary and verify ownership
        self._get_user_itinerary(session, user_id, day.itinerary_id)
        
        crud_itinerary.delete_day(session=session, day_id=day_id)
        return Message(detail="Day deleted successfully")
    
    def add_activity(self, session: Session, user_id: UUID, day_id: int, activity_in: ItineraryActivityCreate) -> ItineraryActivityPublic:
        # Get the day
        day = crud_itinerary.get_day_by_id(session=session, day_id=day_id)
        if not day:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Day not found"
            )
        
        # Get the itinerary and verify ownership
        self._get_user_itinerary(session, user_id, day.itinerary_id)
        
        # Verify place exists
        place = place_service.get_place(session=session, place_id=activity_in.place_id)
        
        activity = crud_itinerary.create_activity(session=session, day_id=day_id, activity_create=activity_in)
        
        # Create ItineraryActivityPublic with place included
        activity_data = activity.dict()
        activity_data["place"] = place
        
        return ItineraryActivityPublic(**activity_data)
    
    def update_activity(self, session: Session, user_id: UUID, activity_id: int, activity_in: ItineraryActivityUpdate) -> ItineraryActivityPublic:
        # Get the activity
        activity = crud_itinerary.get_activity_by_id(session=session, activity_id=activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        # Get the day
        day = crud_itinerary.get_day_by_id(session=session, day_id=activity.day_id)
        if not day:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Day not found"
            )
        
        # Get the itinerary and verify ownership
        self._get_user_itinerary(session, user_id, day.itinerary_id)
        
        # Verify place exists if provided
        place = None
        if activity_in.place_id:
            place = place_service.get_place(session=session, place_id=activity_in.place_id)
        else:
            place = place_service.get_place(session=session, place_id=activity.place_id)
        
        updated_activity = crud_itinerary.update_activity(session=session, db_activity=activity, activity_in=activity_in)
        
        # Create ItineraryActivityPublic with place included
        activity_data = updated_activity.dict()
        activity_data["place"] = place
        
        return ItineraryActivityPublic(**activity_data)
    
    def delete_activity(self, session: Session, user_id: UUID, activity_id: int) -> Message:
        # Get the activity
        activity = crud_itinerary.get_activity_by_id(session=session, activity_id=activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        # Get the day
        day = crud_itinerary.get_day_by_id(session=session, day_id=activity.day_id)
        if not day:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Day not found"
            )
        
        # Get the itinerary and verify ownership
        self._get_user_itinerary(session, user_id, day.itinerary_id)
        
        crud_itinerary.delete_activity(session=session, activity_id=activity_id)
        return Message(detail="Activity deleted successfully")
    
    def _get_user_itinerary(self, session: Session, user_id: UUID, itinerary_id: int) -> Itineraries:
        """Helper method to get an itinerary and verify user ownership"""
        itinerary = crud_itinerary.get_by_id(session=session, itinerary_id=itinerary_id)
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Itinerary not found"
            )
        
        # Verify ownership
        if str(itinerary.user_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this itinerary"
            )
        
        return itinerary

itinerary_service = ItineraryService()