from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from enum import Enum
from models import EventStatus, TicketStatus, PaymentStatus, PaymentMethod


# ==================== ENUMS ====================

class City(str, Enum):
    FREETOWN = "freetown"
    BO = "bo"
    KENEMA = "kenema"
    MAKENI = "makeni"
    KOIDU = "koidu"
    PORT_LOKO = "port_loko"
    WATERLOO = "waterloo"


class UserRole(str, Enum):
    USER = "user"
    ORGANIZER = "organizer"
    VENUE = "venue"
    SPORT = "sport"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationRequestType(str, Enum):
    ORGANIZER = "organizer"
    VENUE = "venue"
    SPORT = "sport"


class BookingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELLED = "cancelled"


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    website: Optional[str] = None
    preferred_city: Optional[City] = None
    preferred_language: str = "en"
    foreigner_mode: bool = False
    role: UserRole = UserRole.USER
    city: Optional[City] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    status: str
    is_verified: bool
    created_at: datetime
    
    artist_profile: Optional["ArtistProfileResponse"] = None
    organizer_profile: Optional["OrganizerProfileResponse"] = None
    business_profile: Optional["BusinessProfileResponse"] = None
    vendor_profile: Optional["VendorProfileResponse"] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    city: City
    phone: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== OTP SCHEMAS ====================

class OTPSend(BaseModel):
    phone: str


class OTPVerify(BaseModel):
    phone: str
    code: str


# ==================== ARTIST SCHEMAS (formerly DJ) ====================

class ArtistProfileBase(BaseModel):
    stage_name: str
    genre: Optional[str] = None
    genre_tags: List[str] = []
    bio: Optional[str] = None
    booking_enabled: bool = False
    spotify_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    artist_type: Optional[str] = "Artist"  # Artist, DJ, or MC


class ArtistProfileCreate(ArtistProfileBase):
    pass


class ArtistProfileResponse(ArtistProfileBase):
    id: int
    user_id: int
    followers_count: int
    events_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Backward compatibility aliases
DJProfileBase = ArtistProfileBase
DJProfileCreate = ArtistProfileCreate
DJProfileResponse = ArtistProfileResponse



# ==================== BUSINESS PROFILE SCHEMAS ====================

class BusinessType(str, Enum):
    CLUB = "club"
    FOOD_SPOT = "food_spot"
    EVENT_VENUE = "event_venue"
    PROMOTER = "promoter"


class BusinessProfileBase(BaseModel):
    business_name: str
    business_type: Optional[List[str]] = []
    description: Optional[str] = None
    website: Optional[str] = None
    city: City


class BusinessProfileCreate(BusinessProfileBase):
    gallery_images: Optional[List[str]] = None


class BusinessProfileResponse(BusinessProfileBase):
    id: int
    user_id: int
    is_verified: bool
    total_revenue: float = 0.0
    events_count: int = 0
    gallery_images: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ORGANIZER PROFILE SCHEMAS ====================

class OrganizerProfileBase(BaseModel):
    organization_name: str
    description: Optional[str] = None
    website: Optional[str] = None


class OrganizerProfileCreate(OrganizerProfileBase):
    pass


class OrganizerProfileResponse(OrganizerProfileBase):
    id: int
    user_id: int
    is_verified: bool = False
    events_count: int = 0
    total_revenue: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CLUB SCHEMAS ====================

class ClubBase(BaseModel):
    name: str
    city: City
    address: str
    description: Optional[str] = None
    is_afrobeat_friendly: bool = False


class ClubCreate(ClubBase):
    pass


class ClubResponse(ClubBase):
    id: int
    cover_image: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== FOOD SPOT SCHEMAS ====================

class FoodSpotBase(BaseModel):
    name: str
    city: City
    address: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None  # $, $$, $$$, $$$$


class FoodSpotCreate(FoodSpotBase):
    pass


class FoodSpotResponse(FoodSpotBase):
    id: int
    cover_image: Optional[str] = None
    is_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VENDOR PROFILE SCHEMAS ====================

class VendorType(str, Enum):
    FOOD = "food"
    MERCH = "merch"
    SERVICE = "service"


class VendorProfileBase(BaseModel):
    business_name: str
    description: Optional[str] = None
    vendor_type: Optional[VendorType] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None


class VendorProfileCreate(VendorProfileBase):
    pass


class VendorProfileResponse(VendorProfileBase):
    id: int
    user_id: int
    rating: float = 0.0
    reviews_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PRODUCT SCHEMAS ====================

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "SLE"
    image_url: Optional[str] = None
    category: Optional[str] = None
    status: str = "active"


class ProductCreate(ProductBase):
    vendor_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    vendor_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== EVENT VENDOR SCHEMAS ====================

class EventVendorBase(BaseModel):
    event_id: int
    vendor_id: int
    booth_location: Optional[str] = None
    status: str = "pending"
    fee_paid: bool = False


class EventVendorCreate(EventVendorBase):
    pass


class EventVendorResponse(EventVendorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VENUE SCHEMAS ====================

class VenueBase(BaseModel):
    name: str
    address: str
    city: City
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    english_friendly: bool = False
    english_menu: bool = False
    accepts_foreign_cards: bool = False
    phone: Optional[str] = None
    category: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    opening_hours: Optional[dict] = None


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: int
    images: Optional[List[str]] = None
    cover_image: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== TICKET TIER SCHEMAS ====================

class TicketTierBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "SLE"
    quantity: int
    max_per_order: int = 10
    sale_start: Optional[datetime] = None
    sale_end: Optional[datetime] = None


class TicketTierCreate(TicketTierBase):
    pass


class TicketTierResponse(TicketTierBase):
    id: int
    event_id: int
    quantity_sold: int
    status: TicketStatus
    
    class Config:
        from_attributes = True


# ==================== EVENT SCHEMAS ====================

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    city: City
    address: Optional[str] = None
    capacity: Optional[int] = None


class EventCreate(EventBase):
    venue_id: Optional[int] = None
    dj_ids: Optional[List[int]] = None
    status: Optional[EventStatus] = None
    flyer_image: Optional[str] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    city: Optional[City] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[EventStatus] = None


class EventResponse(EventBase):
    id: int
    organizer_id: Optional[int] = None
    venue_id: Optional[int] = None
    flyer_image: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    status: EventStatus
    views_count: int
    tickets_sold: int
    share_url: Optional[str] = None
    qr_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    venue: Optional[VenueResponse] = None
    djs: Optional[List[ArtistProfileResponse]] = None
    vendors: Optional[List[EventVendorResponse]] = None
    ticket_tiers: Optional[List["TicketTierResponse"]] = None


class EventListResponse(BaseModel):
    id: int
    title: str
    start_date: datetime
    city: City
    flyer_image: Optional[str] = None
    status: EventStatus
    tickets_sold: int
    capacity: Optional[int] = None
    ticket_tiers: Optional[List[TicketTierResponse]] = None
    
    class Config:
        from_attributes = True




# ==================== TICKET SCHEMAS ====================

class TicketResponse(BaseModel):
    id: int
    user_id: int
    ticket_tier_id: int
    order_id: int
    ticket_number: str
    qr_code: Optional[str] = None
    qr_token: Optional[str] = None  # Secure token for QR code validation
    is_used: bool
    used_at: Optional[datetime] = None
    created_at: datetime
    
    # Include event and ticket_tier information
    event: Optional["EventListResponse"] = None
    ticket_tier: Optional["TicketTierResponse"] = None
    
    # Computed event_id from ticket_tier.event
    event_id: Optional[int] = None
    
    @classmethod
    def from_orm(cls, obj):
        result = super().from_orm(obj)
        # Compute event_id from the event relationship
        if obj.ticket_tier and obj.ticket_tier.event:
            result.event_id = obj.ticket_tier.event.id
        return result
    
    class Config:
        from_attributes = True


class TicketDetailResponse(TicketResponse):
    ticket_tier: TicketTierResponse
    event: Optional[EventListResponse] = None


# ==================== ORDER SCHEMAS ====================

class OrderItem(BaseModel):
    ticket_tier_id: int
    quantity: int


class OrderCreate(BaseModel):
    event_id: int
    items: List[OrderItem]
    payment_method: Optional[PaymentMethod] = None
    attendee_info: Optional[dict] = None
    idempotency_key: Optional[str] = Field(
        None, 
        description="Unique key to prevent duplicate orders. If provided, must be unique per user.",
        max_length=255
    )


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_number: str
    total_amount: float
    currency: str
    payment_method: Optional[PaymentMethod] = None
    payment_status: PaymentStatus
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    tickets: List[TicketResponse]


# ==================== PAYMENT SCHEMAS ====================

class PaymentIntent(BaseModel):
    order_id: int
    amount: float
    currency: str
    payment_method: PaymentMethod


class PaymentConfirm(BaseModel):
    order_id: int
    payment_id: str


class PurchaseTicketData(BaseModel):
    order_id: str
    payment_intent_id: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None


class MobileMoneyCreate(BaseModel):
    order_id: int
    phone_number: str
    provider: str  # orange, africell
    return_url: Optional[str] = None


class CashConfirm(BaseModel):
    order_id: int
    received_amount: float
    notes: Optional[str] = None



# ==================== VERIFICATION SCHEMAS ====================

class VerificationRequestCreate(BaseModel):
    request_type: VerificationRequestType
    documents: List[str]  # URLs to uploaded documents


class VerificationRequestResponse(BaseModel):
    id: int
    user_id: int
    request_type: VerificationRequestType
    status: RequestStatus
    documents: List[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== BOOKING SCHEMAS ====================

class BookingRequestCreate(BaseModel):
    artist_id: int
    event_id: Optional[int] = None
    proposed_date: datetime
    message: Optional[str] = None


class BookingRequestResponse(BaseModel):
    id: int
    artist_id: int
    requester_id: int
    event_id: Optional[int] = None
    proposed_date: datetime
    message: Optional[str] = None
    status: BookingStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ADMIN SCHEMAS ====================

class AdminDashboardStats(BaseModel):
    total_users: int
    total_businesses: int
    total_artists: int
    total_events: int
    total_tickets_sold: int
    total_revenue: float
    pending_verifications: int


class UserFilter(BaseModel):
    role: Optional[UserRole] = None
    city: Optional[City] = None
    is_verified: Optional[bool] = None
    search: Optional[str] = None


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int


class EventModerationAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class EventModerationRequest(BaseModel):
    event_id: int
    action: EventModerationAction
    reason: Optional[str] = None  # Required when rejecting


# ==================== QR CODE SCHEMAS ====================

class QRValidateRequest(BaseModel):
    ticket_number: str


class QRValidateResponse(BaseModel):
    valid: bool
    ticket: Optional[TicketResponse] = None
    message: str


# ==================== SEARCH SCHEMAS ====================

class EventSearch(BaseModel):
    city: Optional[City] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    genre: Optional[str] = None
    query: Optional[str] = None


# ==================== NOTIFICATION SCHEMAS ====================

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== STATS SCHEMAS ====================

class BusinessStats(BaseModel):
    total_events: int
    tickets_sold: int
    total_revenue: float
    platform_commission: float = 0.0
    net_earnings: float = 0.0
    pending_artist_payments: float


class ArtistStats(BaseModel):
    followers: int
    rating: float
    total_gigs: int
    earnings: float


class VendorStats(BaseModel):
    total_sales: float
    active_listings: int
    pending_orders: int
    event_booths: int


class RoleDashboardStats(BaseModel):
    role: UserRole
    business_stats: Optional[BusinessStats] = None
    artist_stats: Optional[ArtistStats] = None
    vendor_stats: Optional[VendorStats] = None


class DashboardStats(BaseModel):
    total_users: int
    total_events: int
    total_tickets_sold: int
    total_revenue: float
    recent_orders: List[OrderResponse]
    popular_events: List[EventListResponse]


class OrganizerStats(BaseModel):
    total_events: int
    total_tickets_sold: int
    total_revenue: float
    upcoming_events: List[EventListResponse]


# ==================== BOOKING SYSTEM SCHEMAS ====================

class BookingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"



# ----- Artist Availability Schemas -----

class ArtistAvailabilityBase(BaseModel):
    date: datetime
    status: str = "available"  # available, booked, unavailable
    note: Optional[str] = None


class ArtistAvailabilityCreate(ArtistAvailabilityBase):
    pass


class ArtistAvailabilityResponse(ArtistAvailabilityBase):
    id: int
    artist_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ----- Artist Review Schemas -----

class ArtistReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    event_type: Optional[str] = None


class ArtistReviewCreate(ArtistReviewBase):
    pass


class ReviewerInfo(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ArtistReviewResponse(ArtistReviewBase):
    id: int
    artist_id: int
    booking_id: int
    reviewer_id: int
    reviewer: Optional[ReviewerInfo] = None
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ----- Booking Message Schemas -----

class BookingMessageBase(BaseModel):
    message: str


class BookingMessageCreate(BookingMessageBase):
    pass


class SenderInfo(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookingMessageResponse(BookingMessageBase):
    id: int
    booking_id: int
    sender_id: int
    sender: Optional[SenderInfo] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ----- Booking Request Schemas -----

class BookingRequestBase(BaseModel):
    artist_id: int
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    event_city: Optional[str] = None
    event_location: Optional[str] = None
    budget: Optional[float] = None
    duration_hours: Optional[int] = None
    message: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    equipment_needed: Optional[List[str]] = None
    travel_required: Optional[bool] = False
    special_requests: Optional[str] = None


class BookingRequestCreate(BookingRequestBase):
    pass


class BookingRequestUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    agreed_price: Optional[float] = None
    payment_method: Optional[str] = None


class ArtistInfo(BaseModel):
    id: int
    stage_name: str
    artist_type: Optional[str] = None
    genre: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookingRequestResponse(BaseModel):
    id: int
    artist_id: int
    artist: Optional[ArtistInfo] = None
    requester_id: int
    requester: Optional[SenderInfo] = None
    event_id: Optional[int] = None
    status: BookingStatus
    
    # Event Details
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    event_city: Optional[str] = None
    event_location: Optional[str] = None
    
    # Booking Details
    budget: Optional[float] = None
    duration_hours: Optional[int] = None
    message: Optional[str] = None
    
    # Contact Info
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Additional
    equipment_needed: Optional[List[str]] = None
    travel_required: Optional[bool] = False
    special_requests: Optional[str] = None
    agreed_price: Optional[float] = None
    payment_method: Optional[str] = None
    
    messages: Optional[List[BookingMessageResponse]] = []
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ----- Detailed Artist Profile Schema -----

class ArtistProfileDetailed(BaseModel):
    id: int
    user_id: int
    stage_name: str
    artist_type: Optional[str] = None
    genre: Optional[str] = None
    genre_tags: Optional[List[str]] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    languages: Optional[List[str]] = None
    city: Optional[str] = None
    
    spotify_url: Optional[str] = None
    soundcloud_url: Optional[str] = None
    
    # Booking settings
    starting_price: Optional[float] = None
    performance_duration: Optional[str] = None
    event_types: Optional[List[str]] = None
    equipment_provided: Optional[List[str]] = None
    travel_availability: Optional[str] = None
    travel_fee: Optional[float] = None
    
    # Stats
    followers_count: int = 0
    events_count: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    is_verified: bool = False
    
    # Related data
    reviews: Optional[List[ArtistReviewResponse]] = []
    
    class Config:
        from_attributes = True



# ═══════════════════════════════════════════════════════════════════════════
# RECAPS SCHEMAS - Event Photo Highlights
# ═══════════════════════════════════════════════════════════════════════════

class RecapStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class RecapCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    photos: List[str] = Field(..., min_items=1, max_items=20)
    event_id: Optional[int] = None


class RecapUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    photos: Optional[List[str]] = Field(None, min_items=1, max_items=20)
    event_id: Optional[int] = None


class RecapResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    photos: List[str]
    views_count: int
    likes_count: int
    status: RecapStatus
    event_id: Optional[int] = None
    organizer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    organizer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class RecapDetailResponse(RecapResponse):
    user_liked: bool = False
    event: Optional[EventListResponse] = None


# ═══════════════════════════════════════════════════════════════════════════
# SIERRA LEONE FEATURES SCHEMAS - Sports, Deals
# ═══════════════════════════════════════════════════════════════════════════

class SportBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: str
    city: City
    location: Optional[str] = None
    date: Optional[datetime] = None

class SportCreate(SportBase):
    pass

class SportResponse(SportBase):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    discount_code: Optional[str] = None
    vendor_id: Optional[int] = None
    venue_id: Optional[int] = None
    expiry_date: Optional[datetime] = None

class DealCreate(DealBase):
    pass

class DealResponse(DealBase):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True


# ==================== SPORTS SCHEMAS ====================

# ==================== MONIME SCHEMAS ====================

class MonimeAmount(BaseModel):
    currency: Optional[str] = None
    value: Optional[int] = None


class MonimeCustomer(BaseModel):
    name: Optional[str] = None


class MonimeRecurrentPaymentTarget(BaseModel):
    expected_payment_count: Optional[int] = Field(default=None, alias="expectedPaymentCount")
    expected_payment_total: Optional[MonimeAmount] = Field(default=None, alias="expectedPaymentTotal")


class MonimeChannelData(BaseModel):
    provider_id: Optional[str] = Field(default=None, alias="providerId")
    account_id: Optional[str] = Field(default=None, alias="accountId")
    reference: Optional[str] = None


class MonimeProcessedPaymentData(BaseModel):
    amount: Optional[MonimeAmount] = None
    order_id: Optional[str] = Field(default=None, alias="orderId")
    payment_id: Optional[str] = Field(default=None, alias="paymentId")
    order_number: Optional[str] = Field(default=None, alias="orderNumber")
    channel_data: Optional[MonimeChannelData] = Field(default=None, alias="channelData")
    financial_transaction_reference: Optional[str] = Field(default=None, alias="financialTransactionReference")
    metadata: Optional[Dict[str, Any]] = None


class MonimeOwnershipOwner(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MonimeOwnershipGraph(BaseModel):
    owner: Optional[MonimeOwnershipOwner] = None


# ── USSD Payment Code ──

class MonimeUssdCode(BaseModel):
    id: Optional[str] = None
    mode: str = "one_time"
    status: str = "pending"
    name: str = ""
    amount: Optional[MonimeAmount] = None
    enable: Optional[bool] = None
    expire_time: Optional[str] = Field(default=None, alias="expireTime")
    customer: Optional[MonimeCustomer] = None
    ussd_code: Optional[str] = Field(default=None, alias="ussdCode")
    reference: Optional[str] = None
    authorized_providers: Optional[List[List[str]]] = Field(default=None, alias="authorizedProviders")
    authorized_phone_number: Optional[str] = Field(default=None, alias="authorizedPhoneNumber")
    recurrent_payment_target: Optional[MonimeRecurrentPaymentTarget] = Field(default=None, alias="recurrentPaymentTarget")
    financial_account_id: Optional[str] = Field(default=None, alias="financialAccountId")
    processed_payment_data: Optional[MonimeProcessedPaymentData] = Field(default=None, alias="processedPaymentData")
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    ownership_graph: Optional[MonimeOwnershipGraph] = Field(default=None, alias="ownershipGraph")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class MonimeUssdCodeCreate(BaseModel):
    name: str
    amount_value: int = Field(..., alias="amountValue")
    currency: str = "SLE"
    mode: str = "one_time"
    duration: str = "10m"
    authorized_providers: Optional[List[str]] = Field(default=None, alias="authorizedProviders")
    authorized_phone_number: Optional[str] = Field(default=None, alias="authorizedPhoneNumber")
    reference: Optional[str] = None
    financial_account_id: Optional[str] = Field(default=None, alias="financialAccountId")
    metadata: Optional[Dict[str, str]] = None
    customer_name: Optional[str] = Field(default=None, alias="customerName")

    class Config:
        populate_by_name = True


# ── Payment / Payout ──

class MonimePayoutSource(BaseModel):
    financial_account_id: Optional[str] = Field(default=None, alias="financialAccountId")
    transaction_reference: Optional[str] = Field(default=None, alias="transactionReference")


class MonimePayoutDestination(BaseModel):
    type: str  # "momo" | "bank" | "wallet"
    provider_id: Optional[str] = Field(default=None, alias="providerId")
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")
    account_number: Optional[str] = Field(default=None, alias="accountNumber")
    branch_code: Optional[str] = Field(default=None, alias="branchCode")
    account_name: Optional[str] = Field(default=None, alias="accountName")


class MonimePayoutFee(BaseModel):
    type: Optional[str] = None
    amount: Optional[MonimeAmount] = None


class MonimeFailureDetail(BaseModel):
    code: str = "unknown"
    message: Optional[str] = None


class MonimePayment(BaseModel):
    id: Optional[str] = None
    status: str = "pending"
    amount: Optional[MonimeAmount] = None
    source: Optional[MonimePayoutSource] = None
    destination: Optional[MonimePayoutDestination] = None
    fees: Optional[List[MonimePayoutFee]] = None
    failure_detail: Optional[MonimeFailureDetail] = Field(default=None, alias="failureDetail")
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    ownership_graph: Optional[MonimeOwnershipGraph] = Field(default=None, alias="ownershipGraph")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class MonimePaymentCreate(BaseModel):
    amount_value: int = Field(..., alias="amountValue")
    currency: str = "SLE"
    destination: MonimePayoutDestination
    source_financial_account_id: Optional[str] = Field(default=None, alias="sourceFinancialAccountId")
    metadata: Optional[Dict[str, str]] = None

    class Config:
        populate_by_name = True


# ── Bank Provider ──

class MonimeBankProvider(BaseModel):
    id: str
    name: str
    country: str = "SL"
    type: str = "bank"
    currency: Optional[str] = None
    supported_currencies: Optional[List[str]] = Field(default=None, alias="supportedCurrencies")
    requires_account_number: bool = Field(default=True, alias="requiresAccountNumber")
    requires_branch_code: bool = Field(default=False, alias="requiresBranchCode")
    active: bool = True

    class Config:
        populate_by_name = True


# ── Webhook Event ──

class MonimeWebhookEventObject(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None


class MonimeWebhookEventData(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    reference: Optional[str] = None
    amount: Optional[MonimeAmount] = None
    failure_detail: Optional[MonimeFailureDetail] = Field(default=None, alias="failureDetail")
    metadata: Optional[Dict[str, Any]] = None


class MonimeWebhookEventPayload(BaseModel):
    api_version: Optional[str] = Field(default=None, alias="apiVersion")
    event: Dict[str, Any] = {}
    object: Optional[MonimeWebhookEventObject] = None
    data: Optional[MonimeWebhookEventData] = None

    class Config:
        populate_by_name = True


class MonimeWebhookLog(BaseModel):
    id: int
    event_id: Optional[str] = None
    event_name: str
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    payload: Dict[str, Any]
    signature: Optional[str] = None
    processed: bool = False
    processing_result: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MonimeWebhookLogCreate(BaseModel):
    event_name: str
    event_id: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    payload: Dict[str, Any]
    signature: Optional[str] = None


# ── Request/Response wrappers ──

class MonimeUssdCodeResponse(BaseModel):
    success: bool
    code_id: Optional[str] = None
    ussd_code: Optional[str] = None
    status: Optional[str] = None
    message: str
    raw: Optional[Dict[str, Any]] = None


class MonimePaymentResponse(BaseModel):
    success: bool
    payment_id: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    destination: Optional[str] = None
    message: str
    raw: Optional[Dict[str, Any]] = None


class MonimeBankListResponse(BaseModel):
    success: bool
    banks: List[MonimeBankProvider]


class MonimeWebhookLogListResponse(BaseModel):
    success: bool
    logs: List[MonimeWebhookLog]
    total: int


# ═══════════════════════════════════════════════════════════════════════════
# POWER BANK SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class PowerBankStationBase(BaseModel):
    name: str
    location_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_units: int = 10
    available_units: int = 10
    price_per_hour: float = 5.0
    max_rental_hours: int = 24


class PowerBankStationCreate(PowerBankStationBase):
    venue_id: Optional[int] = None


class PowerBankStationResponse(PowerBankStationBase):
    id: int
    venue_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PowerBankRentalBase(BaseModel):
    station_id: int
    units_rented: int = 1


class PowerBankRentalCreate(PowerBankRentalBase):
    pass


class PowerBankRentalResponse(BaseModel):
    id: int
    user_id: int
    station_id: int
    units_rented: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    expected_return: Optional[datetime] = None
    total_cost: float
    payment_status: str
    created_at: datetime
    station: Optional[PowerBankStationResponse] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════
# RESTAURANT RESERVATION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class RestaurantReservationBase(BaseModel):
    food_spot_id: int
    reservation_date: date
    reservation_time: str
    party_size: int = 2
    table_number: Optional[str] = None
    special_requests: Optional[str] = None


class RestaurantReservationCreate(RestaurantReservationBase):
    pass


class RestaurantReservationResponse(RestaurantReservationBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    food_spot_name: Optional[str] = None

    class Config:
        from_attributes = True

