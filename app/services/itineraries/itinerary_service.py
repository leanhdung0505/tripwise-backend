from fastapi import HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.models import (
    Message, Itineraries, ItineraryCreate, ItineraryUpdate, ItineraryPublic,
    ItineraryDays, ItineraryDayCreate, ItineraryDayUpdate, ItineraryDayPublic,
    ItineraryActivities, ItineraryActivityCreate, ItineraryActivityUpdate, ItineraryActivityPublic,
    PaginationMetadata, PaginatedResponse, Places, PlacePublic,
    PlacePhotos, RestaurantDetails, HotelDetails, AttractionDetails,
    PlacePhotoPublic, RestaurantDetailPublic, HotelDetailPublic, AttractionDetailPublic
)
from app.crud.itineraries.crud_itinerary import crud_itinerary
from app.services.places.place_service import place_service
from datetime import date

class ItineraryService:
    def _get_place_with_details(self, session: Session, place_id: int) -> PlacePublic:
        """Helper method to get place with all details"""
        # Get the place
        place = session.get(Places, place_id)
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Place with ID {place_id} not found"
            )
        
        # Convert to dict to build PlacePublic
        place_data = place.dict()
        
        # Get photos
        photos = session.exec(
            select(PlacePhotos).where(PlacePhotos.place_id == place_id)
        ).all()
        place_data["photos"] = [PlacePhotoPublic(**photo.dict()) for photo in photos] if photos else []
        
        # Get details based on place type
        place_data["restaurant_detail"] = None
        place_data["hotel_detail"] = None
        place_data["attraction_detail"] = None
        
        if place.type.upper() == "RESTAURANT":
            restaurant_detail = session.exec(
                select(RestaurantDetails).where(RestaurantDetails.place_id == place_id)
            ).first()
            if restaurant_detail:
                place_data["restaurant_detail"] = RestaurantDetailPublic(**restaurant_detail.dict())
        
        elif place.type.upper() == "HOTEL":
            hotel_detail = session.exec(
                select(HotelDetails).where(HotelDetails.place_id == place_id)
            ).first()
            if hotel_detail:
                place_data["hotel_detail"] = HotelDetailPublic(**hotel_detail.dict())
        
        elif place.type.upper() == "ATTRACTION":
            attraction_detail = session.exec(
                select(AttractionDetails).where(AttractionDetails.place_id == place_id)
            ).first()
            if attraction_detail:
                place_data["attraction_detail"] = AttractionDetailPublic(**attraction_detail.dict())
        
        return PlacePublic(**place_data)

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

            # Add activities for this day
            activities = crud_itinerary.get_activities(session=session, day_id=day.day_id)
            activities_with_place = []

            for activity in activities:
                activity_data = activity.dict()
                # Use the new method to get place with all details
                place = self._get_place_with_details(session=session, place_id=activity.place_id)
                activity_data["place"] = place
                activities_with_place.append(ItineraryActivityPublic(**activity_data))

            day_data["activities"] = activities_with_place
            days_with_data.append(ItineraryDayPublic(**day_data))

        # Create ItineraryPublic with days included
        itinerary_data = itinerary.dict()
        itinerary_data["days"] = days_with_data

        # Lấy hotel nếu có với đầy đủ thông tin chi tiết
        itinerary_data["hotel"] = None
        if itinerary.hotel_id:
            itinerary_data["hotel"] = self._get_place_with_details(session=session, place_id=itinerary.hotel_id)

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
            # Include basic itinerary data with hotel details if available
            itinerary_data = itinerary.dict()
            itinerary_data["days"] = []  # Empty for list view
            
            # Add hotel details if present
            itinerary_data["hotel"] = None
            if itinerary.hotel_id:
                itinerary_data["hotel"] = self._get_place_with_details(session=session, place_id=itinerary.hotel_id)
            
            itineraries_with_data.append(ItineraryPublic(**itinerary_data))
        
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
        
        # Validate hotel exists if provided
        if itinerary_in.hotel_id:
            self._get_place_with_details(session=session, place_id=itinerary_in.hotel_id)
        
        itinerary = crud_itinerary.create(session=session, itinerary_create=itinerary_in, user_id=str(user_id))
        
        # Add empty days list and hotel details as it's a new itinerary
        itinerary_data = itinerary.dict()
        itinerary_data["days"] = []
        itinerary_data["hotel"] = None
        if itinerary.hotel_id:
            itinerary_data["hotel"] = self._get_place_with_details(session=session, place_id=itinerary.hotel_id)
        
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
        
        # Validate hotel exists if provided
        if itinerary_in.hotel_id:
            self._get_place_with_details(session=session, place_id=itinerary_in.hotel_id)
        
        updated_itinerary = crud_itinerary.update(session=session, db_itinerary=itinerary, itinerary_in=itinerary_in)
        
        # Return the updated itinerary with all details
        return self.get_itinerary(session=session, itinerary_id=itinerary_id)
    
    def delete_itinerary(self, session: Session, user_id: UUID, itinerary_id: int) -> Message:
    # Get the itinerary and verify ownership
        itinerary = self._get_user_itinerary(session, user_id, itinerary_id)

        # Xóa tất cả các ngày và hoạt động liên quan
        days = crud_itinerary.get_days(session=session, itinerary_id=itinerary_id)
        for day in days:
            # Xóa tất cả activity của day này
            activities = crud_itinerary.get_activities(session=session, day_id=day.day_id)
            for activity in activities:
                crud_itinerary.delete_activity(session=session, activity_id=activity.itinerary_activity_id)
            crud_itinerary.delete_day(session=session, day_id=day.day_id)

        # Sau khi đã xóa hết các bản ghi con, mới xóa itinerary
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
        
        updated_day = crud_itinerary.update_day(session=session, db_day=day, day_in=day_in)
        
        # Fetch activities for this day with full place details
        activities = crud_itinerary.get_activities(session=session, day_id=day_id)
        activities_with_place = []
        
        for activity in activities:
            activity_data = activity.dict()
            place = self._get_place_with_details(session=session, place_id=activity.place_id)
            activity_data["place"] = place
            activities_with_place.append(ItineraryActivityPublic(**activity_data))
        
        # Create ItineraryDayPublic with activities included
        day_data = updated_day.dict()
        day_data["activities"] = activities_with_place
        
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
        itinerary = self._get_user_itinerary(session, user_id, day.itinerary_id)

        # Lưu lại day_number và itinerary_id trước khi xóa
        deleted_day_number = day.day_number
        itinerary_id = day.itinerary_id

        # Xóa day
        crud_itinerary.delete_day(session=session, day_id=day_id)

        # Lấy lại tất cả các ngày còn lại, sắp xếp theo day_number
        days = crud_itinerary.get_days(session=session, itinerary_id=itinerary_id)

        # Cập nhật lại day_number và date cho các ngày sau ngày vừa xóa
        from datetime import timedelta

        # Tìm ngày bắt đầu của itinerary
        start_date = itinerary.start_date

        for idx, d in enumerate(days):
            new_day_number = idx + 1
            new_date = start_date + timedelta(days=idx)
            if d.day_number != new_day_number or d.date != new_date:
                d.day_number = new_day_number
                d.date = new_date
                session.add(d)
        session.commit()

        return Message(detail="Day deleted and subsequent days updated successfully")
    
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
        
        # Verify place exists and get full details
        place = self._get_place_with_details(session=session, place_id=activity_in.place_id)
        
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
        
        # Verify place exists if provided and get full details
        place = None
        if activity_in.place_id:
            place = self._get_place_with_details(session=session, place_id=activity_in.place_id)
        else:
            place = self._get_place_with_details(session=session, place_id=activity.place_id)
        
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