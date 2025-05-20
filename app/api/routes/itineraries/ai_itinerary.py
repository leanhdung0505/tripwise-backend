from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Any
from uuid import UUID
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ItineraryPublic, ItineraryCreate, ItineraryDayCreate, ItineraryActivityCreate,
    Message
)
from datetime import timedelta
from app.services.itineraries.itinerary_service import itinerary_service
from datetime import datetime, time

router = APIRouter(prefix="/itinerary-planner", tags=["itinerary-planner"])

# Default start times for activities based on their order
DEFAULT_START_TIMES = [
    time(7, 30),  # 7:30
    time(8, 30),  # 8:30
    time(11, 30), # 11:30
    time(14, 0),  # 14:00
    time(17, 0),  # 17:00
    time(20, 0),  # 20:00
]

@router.post("/create-from-ai", response_model=ItineraryPublic)
def create_itinerary_from_ai(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    ai_data: Dict[str, Any] = Body(...)
) -> ItineraryPublic:
    """
    Create a new itinerary from AI-generated data format.
    Automatically assigns start times to activities.
    """
    # Handle date format - convert string dates to proper date objects
    try:
        start_date = datetime.fromisoformat(ai_data.get("start_date")).date()
        end_date = datetime.fromisoformat(ai_data.get("end_date")).date()
    except (ValueError, TypeError):
        # Fallback to current date if dates are invalid
        current_date = datetime.now().date()
        start_date = current_date
        end_date = current_date
    
    # Create base itinerary
    itinerary_data = ItineraryCreate(
        title=ai_data.get("tile", "AI Generated Itinerary"),  # Handle typo in input (tile → title)
        description=ai_data.get("description", "Generated from AI planning"),
        start_date=start_date,
        end_date=end_date,
        budget=ai_data.get("budget", "0"),
        destination_city=ai_data.get("destination_city", "Unknown"),
        is_favorite=False,
        is_completed=False,
        hotel_id=ai_data.get("hotel_id")
    )
    
    # Create the itinerary first
    itinerary = itinerary_service.create_itinerary(
        session=session,
        user_id=current_user.user_id,
        itinerary_in=itinerary_data
    )
    
    # Process days and activities
    days_data = ai_data.get("days", [])
    for day_info in days_data:
        day_number = day_info.get("day_number", 1)
        day_date = start_date + timedelta(days=day_number - 1)

        # Create day
        day_data = ItineraryDayCreate(
            day_number=day_number,
            date=day_date,
        )

        day = itinerary_service.add_day(
            session=session,
            user_id=current_user.user_id,
            itinerary_id=itinerary.itinerary_id,
            day_in=day_data
        )
        
        # Process activities for this day
        activities = day_info.get("activities", [])
        for idx, activity in enumerate(activities):
            if idx < len(DEFAULT_START_TIMES):
                start_time = DEFAULT_START_TIMES[idx]
            else:
                # Default to last time slot if more activities than time slots
                start_time = DEFAULT_START_TIMES[-1]
                
            # Create activity
            activity_data = ItineraryActivityCreate(
                place_id=activity.get("place_id"),
                start_time=start_time
            )
            
            itinerary_service.add_activity(
                session=session,
                user_id=current_user.user_id,
                day_id=day.day_id,
                activity_in=activity_data
            )
    
    # Return the full itinerary with all days and activities
    return itinerary_service.get_itinerary(
        session=session,
        itinerary_id=itinerary.itinerary_id
    )