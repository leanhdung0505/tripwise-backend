from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, col
from app.models import (
    Itineraries, ItineraryCreate, ItineraryUpdate,
    ItineraryDays, ItineraryDayCreate, ItineraryDayUpdate,
    ItineraryActivities, ItineraryActivityCreate, ItineraryActivityUpdate,
    Places
)
from datetime import datetime

class CRUDItinerary:
    def get_by_id(self, session: Session, itinerary_id: int) -> Optional[Itineraries]:
        return session.get(Itineraries, itinerary_id)
    
    def get_multi(self, session: Session, skip: int = 0, limit: int = 100) -> List[Itineraries]:
        return session.exec(select(Itineraries).offset(skip).limit(limit)).all()
    
    def get_by_user_id(self, session: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Itineraries]:
        return session.exec(
            select(Itineraries)
            .where(Itineraries.user_id == user_id)
            .order_by(col(Itineraries.created_at).desc())
            .offset(skip)
            .limit(limit)
        ).all()
    
    def get_by_destination(self, session: Session, destination: str, skip: int = 0, limit: int = 100) -> List[Itineraries]:
        return session.exec(
            select(Itineraries)
            .where(Itineraries.destination_city == destination)
            .offset(skip)
            .limit(limit)
        ).all()
    
    def create(self, session: Session, itinerary_create: ItineraryCreate, user_id: str) -> Itineraries:
        db_obj = Itineraries(
            user_id=user_id,
            title=itinerary_create.title,
            description=itinerary_create.description,
            start_date=itinerary_create.start_date,
            end_date=itinerary_create.end_date,
            budget=itinerary_create.budget,
            destination_city=itinerary_create.destination_city,
            is_favorite=itinerary_create.is_favorite,
            is_completed=itinerary_create.is_completed,
            hotel_id=itinerary_create.hotel_id
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update(self, session: Session, db_itinerary: Itineraries, itinerary_in: ItineraryUpdate) -> Itineraries:
        update_data = itinerary_in.model_dump(exclude_unset=True)
        db_itinerary.sqlmodel_update(update_data)
        db_itinerary.updated_at = datetime.now()
        session.add(db_itinerary)
        session.commit()
        session.refresh(db_itinerary)
        return db_itinerary
    
    def delete(self, session: Session, itinerary_id: int) -> None:
        db_obj = session.get(Itineraries, itinerary_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()

    def get_days(self, session: Session, itinerary_id: int) -> List[ItineraryDays]:
        return session.exec(
            select(ItineraryDays)
            .where(ItineraryDays.itinerary_id == itinerary_id)
            .order_by(ItineraryDays.day_number)
        ).all()
    
    def get_day_by_id(self, session: Session, day_id: int) -> Optional[ItineraryDays]:
        return session.get(ItineraryDays, day_id)
    
    def create_day(self, session: Session, itinerary_id: int, day_create: ItineraryDayCreate) -> ItineraryDays:
        db_obj = ItineraryDays(
            itinerary_id=itinerary_id,
            day_number=day_create.day_number,
            date=day_create.date,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update_day(self, session: Session, db_day: ItineraryDays, day_in: ItineraryDayUpdate) -> ItineraryDays:
        update_data = day_in.model_dump(exclude_unset=True)
        db_day.sqlmodel_update(update_data)
        db_day.updated_at = datetime.now()
        session.add(db_day)
        session.commit()
        session.refresh(db_day)
        return db_day
    
    def delete_day(self, session: Session, day_id: int) -> None:
        db_obj = session.get(ItineraryDays, day_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
    
    def get_activities(self, session: Session, day_id: int) -> List[ItineraryActivities]:
        return session.exec(
            select(ItineraryActivities)
            .where(ItineraryActivities.day_id == day_id)
            .order_by(ItineraryActivities.start_time)
        ).all()
    
    def get_activity_by_id(self, session: Session, activity_id: int) -> Optional[ItineraryActivities]:
        return session.get(ItineraryActivities, activity_id)
    
    def create_activity(self, session: Session, day_id: int, activity_create: ItineraryActivityCreate) -> ItineraryActivities:
        db_obj = ItineraryActivities(
            day_id=day_id,
            place_id=activity_create.place_id,
            start_time=activity_create.start_time
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    def update_activity(self, session: Session, db_activity: ItineraryActivities, activity_in: ItineraryActivityUpdate) -> ItineraryActivities:
        update_data = activity_in.model_dump(exclude_unset=True)
        db_activity.sqlmodel_update(update_data)
        db_activity.updated_at = datetime.now()
        session.add(db_activity)
        session.commit()
        session.refresh(db_activity)
        return db_activity
    
    def delete_activity(self, session: Session, activity_id: int) -> None:
        db_obj = session.get(ItineraryActivities, activity_id)
        if db_obj:
            session.delete(db_obj)
            session.commit()


# Create and export an instance
crud_itinerary = CRUDItinerary()

# Make sure to export the instance
__all__ = ["crud_itinerary"]