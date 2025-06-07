from sqlmodel import Session, select
from app.models import FavoriteItineraries

class CRUDFavoriteItinerary:
    def add(self, session: Session, user_id, itinerary_id):
        fav = session.exec(
            select(FavoriteItineraries).where(
                (FavoriteItineraries.user_id == user_id) &
                (FavoriteItineraries.itinerary_id == itinerary_id)
            )
        ).first()
        if fav:
            return fav  # Đã có rồi
        fav = FavoriteItineraries(user_id=user_id, itinerary_id=itinerary_id)
        session.add(fav)
        session.commit()
        session.refresh(fav)
        return fav

    def remove(self, session: Session, user_id, itinerary_id):
        fav = session.exec(
            select(FavoriteItineraries).where(
                (FavoriteItineraries.user_id == user_id) &
                (FavoriteItineraries.itinerary_id == itinerary_id)
            )
        ).first()
        if fav:
            session.delete(fav)
            session.commit()
        return fav

    def get_favorites(self, session: Session, user_id):
        return session.exec(
            select(FavoriteItineraries).where(FavoriteItineraries.user_id == user_id)
        ).all()

crud_favorite = CRUDFavoriteItinerary()