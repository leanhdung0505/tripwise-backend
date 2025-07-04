import uuid
from datetime import datetime, date as date_type, time as time_type
from typing import List, Dict, Any, Literal, Optional, TypeVar, Generic
from pydantic import EmailStr, Field as PydanticField, BaseModel
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, UniqueConstraint, Text, Time, Date
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY


# Generic Response Model with data wrapper
T = TypeVar('T')

class ResponseWrapper(SQLModel, Generic[T]):
    data: T
class PaginationMetadata(SQLModel):
    page: int
    limit: int
    total_pages: int
    has_prev: bool
    has_next: bool

class PaginatedResponse(SQLModel, Generic[T]):
    data: List[T]
    pagination: PaginationMetadata



# Database Models
class Users(SQLModel, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True)
    email: str = Field(max_length=100, unique=True)
    password: str = Field(max_length=255)  # Changed from password_hash to match SQL
    full_name: str = Field(max_length=100)
    role: str = Field(max_length=20, default="user")  # Added to match SQL
    profile_picture: str | None = Field(max_length=255, default=None)  # Changed from avt_img
    preferences: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    budget_preference: int | None = Field(default=None)
    is_active: bool = Field(default=True)  # Added is_active field
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    itineraries: List["Itineraries"] = Relationship(back_populates="user")
    shared_itineraries: List["ItineraryShares"] = Relationship(
        back_populates="shared_with_user",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    fcm_tokens: List["FCMTokens"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    favorite_itineraries: List["FavoriteItineraries"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )

class Places(SQLModel, table=True):
    __tablename__ = "places"

    place_id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    local_name: str | None = Field(max_length=100, default=None)
    description: str | None = Field(sa_column=Column(Text), default=None)
    type: str = Field(max_length=50)  # RESTAURANT, HOTEL, ATTRACTION
    address: str | None = Field(sa_column=Column(Text), default=None)
    city: str = Field(max_length=100)
    latitude: float = Field()
    longitude: float = Field()
    rating: float | None = Field(default=None)
    price_range: str | None = Field(max_length=20, default=None)
    phone: str | None = Field(max_length=30, default=None)
    email: str | None = Field(max_length=100, default=None)
    website: str | None = Field(max_length=255, default=None)
    web_url: str | None = Field(max_length=255, default=None)
    image: str | None = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    number_review: int | None = Field(default=None)


    # Relationships
    photos: List["PlacePhotos"] = Relationship(back_populates="place")
    restaurant_detail: Optional["RestaurantDetails"] = Relationship(back_populates="place")
    hotel_detail: Optional["HotelDetails"] | None = Relationship(back_populates="place")
    attraction_detail: Optional["AttractionDetails"] | None = Relationship(back_populates="place")
    itinerary_activities: List["ItineraryActivities"] = Relationship(back_populates="place")
    itineraries: List["Itineraries"] = Relationship(back_populates="hotel")


class PlacePhotos(SQLModel, table=True):
    __tablename__ = "place_photos"

    photo_id: int = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="places.place_id")
    photo_url: str = Field(max_length=255)
    is_primary: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    place: Places = Relationship(back_populates="photos")


class RestaurantDetails(SQLModel, table=True):
    __tablename__ = "restaurant_details"

    restaurant_detail_id: int = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="places.place_id")
    meal_types: List[str] = Field(sa_column=Column(ARRAY(Text)))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    place: Places = Relationship(back_populates="restaurant_detail")


class HotelDetails(SQLModel, table=True):
    __tablename__ = "hotel_details"

    hotel_detail_id: int = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="places.place_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    place: Places = Relationship(back_populates="hotel_detail")


class AttractionDetails(SQLModel, table=True):
    __tablename__ = "attraction_details"

    attraction_detail_id: int = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="places.place_id")
    subcategory: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    subtype: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    place: Places = Relationship(back_populates="attraction_detail")


class Itineraries(SQLModel, table=True):
    __tablename__ = "itineraries"

    itinerary_id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    title: str = Field(max_length=100)
    description: str | None = Field(sa_column=Column(Text), default=None)
    start_date: date_type = Field(sa_column=Column(Date))
    end_date: date_type = Field(sa_column=Column(Date))
    budget: str | None = Field(default=None)
    destination_city: str = Field(max_length=100, default="Da Nang")
    is_favorite: bool = Field(default=False)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    hotel_id: int | None = Field(foreign_key="places.place_id", default=None)


    # Relationships
    user: Users = Relationship(back_populates="itineraries")
    days: List["ItineraryDays"] = Relationship(back_populates="itinerary", sa_relationship_kwargs={"cascade": "all, delete"})   
    hotel: Places | None = Relationship(back_populates="itineraries")
    shares: List["ItineraryShares"] = Relationship(
        back_populates="itinerary", 
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    favorite_by: List["FavoriteItineraries"] = Relationship(
        back_populates="itinerary",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )

class ItineraryDays(SQLModel, table=True):
    __tablename__ = "itinerary_days"

    day_id: int = Field(default=None, primary_key=True)
    itinerary_id: int = Field(foreign_key="itineraries.itinerary_id")
    day_number: int = Field()
    date: date_type = Field(sa_column=Column(Date))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    itinerary: Itineraries = Relationship(back_populates="days")
    activities: List["ItineraryActivities"] = Relationship(
        back_populates="day",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )

class ItineraryActivities(SQLModel, table=True):
    __tablename__ = "itinerary_activities"

    itinerary_activity_id: int = Field(default=None, primary_key=True)
    day_id: int = Field(foreign_key="itinerary_days.day_id")
    place_id: int = Field(foreign_key="places.place_id")
    start_time: time_type = Field(sa_column=Column(Time))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    day: ItineraryDays = Relationship(back_populates="activities")
    place: Places = Relationship(back_populates="itinerary_activities")

class ItineraryShares(SQLModel, table=True):
    __tablename__ = "itinerary_shares"

    share_id: int = Field(default=None, primary_key=True)
    itinerary_id: int = Field(foreign_key="itineraries.itinerary_id")
    shared_with_user_id: uuid.UUID = Field(foreign_key="users.user_id")
    permission: str = Field(max_length=10, default="view")  # view, edit
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    itinerary: Itineraries = Relationship(back_populates="shares")
    shared_with_user: Users = Relationship(back_populates="shared_itineraries")
class FCMTokens(SQLModel, table=True):
    __tablename__ = "fcm_tokens"

    token_id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    fcm_token: str = Field(max_length=255)
    device: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_used_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: Users = Relationship(back_populates="fcm_tokens")
class FavoriteItineraries(SQLModel, table=True):
    __tablename__ = "favorite_itineraries"

    favorite_id: int = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.user_id")
    itinerary_id: int = Field(foreign_key="itineraries.itinerary_id")
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: "Users" = Relationship(back_populates="favorite_itineraries")
    itinerary: "Itineraries" = Relationship(back_populates="favorite_by")
# API Request/Response Models
class PlaceBase(SQLModel):
    name: str
    local_name: str | None = None
    description: str | None = None
    type: str
    address: str | None = None
    city: str
    latitude: float
    longitude: float
    rating: float | None = None
    price_range: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    web_url: str | None = None
    image: str | None = None
    number_review : int | None = None



class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(SQLModel):
    name: str | None = None
    local_name: str | None = None
    description: str | None = None
    type: str | None = None
    address: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None
    price_range: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    web_url: str | None = None
    image: str | None = None


class PlacePhotoBase(SQLModel):
    photo_url: str
    is_primary: bool = False


class PlacePhotoCreate(PlacePhotoBase):
    pass


class PlacePhotoPublic(PlacePhotoBase):
    photo_id: int
    place_id: int
    created_at: datetime


class PlacePhotoResponse(ResponseWrapper[PlacePhotoPublic]):
    pass


class RestaurantDetailBase(SQLModel):
    meal_types: List[str]


class RestaurantDetailCreate(RestaurantDetailBase):
    pass


class RestaurantDetailUpdate(SQLModel):
    meal_types: List[str] | None = None


class RestaurantDetailPublic(RestaurantDetailBase):
    restaurant_detail_id: int
    place_id: int
    created_at: datetime
    updated_at: datetime


class RestaurantDetailResponse(ResponseWrapper[RestaurantDetailPublic]):
    pass


class HotelDetailBase(SQLModel):
    pass


class HotelDetailCreate(HotelDetailBase):
    pass


class HotelDetailUpdate(SQLModel):
    pass


class HotelDetailPublic(HotelDetailBase):
    hotel_detail_id: int
    place_id: int
    created_at: datetime
    updated_at: datetime


class HotelDetailResponse(ResponseWrapper[HotelDetailPublic]):
    pass

class AttractionDetailBase(SQLModel):
    subcategory: Dict[str, Any] | None = None
    subtype: Dict[str, Any] | None = None


class AttractionDetailCreate(AttractionDetailBase):
    pass


class AttractionDetailUpdate(SQLModel):
    subcategory: Dict[str, Any] | None = None
    subtype: Dict[str, Any] | None = None


class AttractionDetailPublic(AttractionDetailBase):
    attraction_detail_id: int
    place_id: int
    created_at: datetime
    updated_at: datetime


class AttractionDetailResponse(ResponseWrapper[AttractionDetailPublic]):
    pass


class PlacePublic(PlaceBase):
    place_id: int
    created_at: datetime
    updated_at: datetime
    photos: List[PlacePhotoPublic] | None = None
    restaurant_detail: RestaurantDetailPublic | None = None
    hotel_detail: HotelDetailPublic | None = None
    attraction_detail: AttractionDetailPublic | None = None


class PlaceResponse(ResponseWrapper[PlacePublic]):
    pass


class PlacesResponse(SQLModel):
    count: int
    data: List[PlacePublic]


class ItineraryBase(SQLModel):
    title: str
    description: str | None = None
    start_date: date_type
    end_date: date_type
    budget: str | None = None
    destination_city: str = "Da Nang"
    is_favorite: bool = False
    is_completed: bool = False
    hotel_id: int | None = None



class ItineraryCreate(ItineraryBase):
    pass


class ItineraryUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    budget: Optional[str] = None
    destination_city: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_completed: Optional[bool] = None
    hotel_id: Optional[int] = None 

class ItineraryDayBase(SQLModel):
    day_number: Optional[int] = None
    date: date_type


class ItineraryDayCreate(ItineraryDayBase):
    pass


class ItineraryDayUpdate(SQLModel):
    day_number: Optional[int] = None
    date: Optional[date_type] = None


class ItineraryActivityBase(SQLModel):
    place_id: int
    start_time: time_type


class ItineraryActivityCreate(ItineraryActivityBase):
    pass


class ItineraryActivityUpdate(SQLModel):
    place_id: Optional[int] = None
    start_time: Optional[time_type] = None


class ItineraryActivityPublic(ItineraryActivityBase):
    itinerary_activity_id: int
    day_id: int
    created_at: datetime
    updated_at: datetime
    place: PlacePublic


class ItineraryActivityResponse(ResponseWrapper[ItineraryActivityPublic]):
    pass


class ItineraryDayPublic(ItineraryDayBase):
    day_id: int
    itinerary_id: int
    created_at: datetime
    updated_at: datetime
    activities: List[ItineraryActivityPublic] | None = None


class ItineraryDayResponse(ResponseWrapper[ItineraryDayPublic]):
    pass


class UserPublicMinimal(SQLModel):
    user_id: uuid.UUID
    username: str
    full_name: str
    email: str
    profile_picture: str | None = None
    permissions : Optional[str] = None
    
class ItineraryPublic(ItineraryBase):
    itinerary_id: int
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    hotel: PlacePublic | None = None
    days: List[ItineraryDayPublic] | None = None
    shared_users: List[UserPublicMinimal] | None = None  
    owner: UserPublicMinimal | None = None


class ItineraryResponse(ResponseWrapper[ItineraryPublic]):
    pass


class ItinerariesResponse(SQLModel):
    count: int
    data: List[ItineraryPublic]


# Itinerary Share Models
class ItineraryShareBase(SQLModel):
    itinerary_id: int
    shared_with_user_id: uuid.UUID
    permission: str = Field(default="view", description="Permission level: view or edit")


class ItineraryShareCreate(ItineraryShareBase):
    pass


class ItineraryShareUpdate(SQLModel):
    permission: Optional[str] = Field(None, description="Permission level: view or edit")

class ItineraryPublicMinimal(SQLModel):
    itinerary_id: int
    title: str
    description: str | None = None
    start_date: date_type
    end_date: date_type
    destination_city: str


class ItinerarySharePublic(ItineraryShareBase):
    share_id: int
    created_at: datetime
    updated_at: datetime
    shared_with_user: UserPublicMinimal | None = None
    itinerary: ItineraryPublicMinimal | None = None


class ItineraryShareResponse(ResponseWrapper[ItinerarySharePublic]):
    pass


class ItinerarySharesResponse(PaginatedResponse[ItinerarySharePublic]):
    pass


# Authentication models
class ChangePassword(SQLModel):
    old_password: str
    new_password: str = PydanticField(
        min_length=8,
        max_length=40,
        description="New password must be between 8 and 40 characters"
    )


class NewPassword(SQLModel):
    email: EmailStr = PydanticField(
        description="Email that was verified through OTP"
    )
    new_password: str = PydanticField(
        min_length=8,
        max_length=40,
        description="New password must be between 8 and 40 characters"
    )


class OTPRequest(SQLModel):
    email: EmailStr
    purpose: Literal["register", "recovery"]


class OTPResponseData(SQLModel):
    message: str
    token: str


class OTPResponse(ResponseWrapper[OTPResponseData]):
    data: OTPResponseData


class OTPVerify(SQLModel):
    token: str
    otp_code: str = PydanticField(..., min_length=5, max_length=5, pattern="^[0-9]+$")


class OTPVerifyPublic(SQLModel):
    message: str
    email: EmailStr


class OTPVerifyResponse(ResponseWrapper[OTPVerifyPublic]):
    pass

class ImageUploadPublic(SQLModel):
    image_url: str
class ImageUploadResponse(ResponseWrapper[ImageUploadPublic]):
    pass
class Message(SQLModel):
    detail: str

class GoogleLoginRequest(BaseModel):
    token: str  # Google ID token từ frontend
    fcm_token: Optional[str] = None  # FCM token for push notifications
    device: Optional[str] = None 
class GoogleUserInfo(BaseModel):
    id: str
    email: str
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None  # <-- sửa thành Optional


class SharePermissionUpdate(BaseModel):
    shared_with_user_id: uuid.UUID
    permission: str

class SharePermissionsUpdateRequest(BaseModel):
    itinerary_id: int
    updates: list[SharePermissionUpdate]
    
__all__ = [
    # Generic Wrapper
    "ResponseWrapper",
    "PaginatedResponse",
    "PaginationMetadata",
    
    # Database Models
    "Users",
    "Places",
    "PlacePhotos",
    "RestaurantDetails",
    "HotelDetails",
    "AttractionDetails",
    "Itineraries",
    "ItineraryDays",
    "ItineraryActivities",
    "ItineraryShares",
    
    # User Models
    "UserBase",
    "UserPublic",
    "UsersPublic",
    "UserLogin",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UserResponse",
    "UserPublicMinimal",
    
    # Place Models
    "PlaceBase",
    "PlaceCreate", 
    "PlaceUpdate",
    "PlacePublic",
    "PlaceResponse",
    
    # Place Photos Models
    "PlacePhotoBase",
    "PlacePhotoCreate",
    "PlacePhotoPublic",
    "PlacePhotoResponse",
    
    # Restaurant Details Models
    "RestaurantDetailBase",
    "RestaurantDetailCreate",
    "RestaurantDetailUpdate",
    "RestaurantDetailPublic",
    "RestaurantDetailResponse",
    
    # Hotel Details Models
    "HotelDetailBase",
    "HotelDetailCreate",
    "HotelDetailUpdate",
    "HotelDetailPublic",
    "HotelDetailResponse",
    
    # Attraction Details Models
    "AttractionDetailBase",
    "AttractionDetailCreate",
    "AttractionDetailUpdate",
    "AttractionDetailPublic",
    "AttractionDetailResponse",
    
    # Itinerary Models
    "ItineraryBase",
    "ItineraryCreate",
    "ItineraryUpdate",
    "ItineraryPublic",
    "ItineraryPublicMinimal",
    "ItineraryResponse",
    "ItinerariesResponse",
    "FavoriteItineraries",
    
    # Itinerary Day Models
    "ItineraryDayBase",
    "ItineraryDayCreate",
    "ItineraryDayUpdate",
    "ItineraryDayPublic",
    "ItineraryDayResponse",
    
    # Itinerary Activity Models
    "ItineraryActivityBase",
    "ItineraryActivityCreate",
    "ItineraryActivityUpdate",
    "ItineraryActivityPublic",
    "ItineraryActivityResponse",
    
    # Itinerary Share Models
    "ItineraryShareBase",
    "ItineraryShareCreate",
    "ItineraryShareUpdate",
    "ItinerarySharePublic",
    "ItineraryShareResponse",
    "ItinerarySharesResponse",
    
    # Authentication Models
    "Token",
    "TokenPayload",
    "ChangePassword",
    "NewPassword",
    "OTPRequest",
    "OTPResponse",
    "OTPVerify",
    "OTPVerifyPublic",
    "OTPVerifyResponse",
    "Message",
    "GoogleLoginRequest",
    "GoogleUserInfo"
]