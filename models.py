from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ORGANIZER = "organizer"
    VENUE = "venue"
    SPORT = "sport"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class TicketStatus(str, enum.Enum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    LIMITED = "limited"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    STRIPE = "stripe"
    MOBILE_MONEY = "mobile_money"
    ORANGE_MONEY = "orange_money"
    AFRICELL_MONEY = "africell_money"
    CASH_AT_VENUE = "cash_at_venue"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"


class City(str, enum.Enum):
    FREETOWN = "freetown"
    BO = "bo"
    KENEMA = "kenema"
    MAKENI = "makeni"
    KOIDU = "koidu"
    PORT_LOKO = "port_loko"
    WATERLOO = "waterloo"


class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationType(str, enum.Enum):
    ORGANIZER = "organizer"
    VENUE = "venue"
    SPORT = "sport"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    FINANCE_ADMIN = "finance_admin"
    OPERATIONS_ADMIN = "operations_admin"
    MARKETING_ADMIN = "marketing_admin"
    SUPPORT_ADMIN = "support_admin"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class RecapStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class FixtureStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    HALFTIME = "halftime"
    COMPLETED = "completed"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class MatchEventType(str, enum.Enum):
    GOAL = "goal"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    SUBSTITUTION = "substitution"
    INJURY = "injury"
    PENALTY = "penalty"


class LeagueStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    UPCOMING = "upcoming"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    
    # Social auth
    google_id = Column(String(255), unique=True, nullable=True)
    apple_id = Column(String(255), unique=True, nullable=True)
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    background_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    instagram = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Role & Status
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_verified = Column(Boolean, default=False)
    reset_token_nonce = Column(String(64), nullable=True)
    
    # Preferences
    preferred_city = Column(Enum(City), nullable=True)
    preferred_language = Column(String(10), default="en")
    notifications_enabled = Column(Boolean, default=True)
    
    # Foreigner mode
    foreigner_mode = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships - ONLY for Sierra Leone Ecosystem
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id")
    organizer_profile = relationship("OrganizerProfile", back_populates="user", uselist=False)
    venue_profile = relationship("VenueProfile", back_populates="user", uselist=False)
    sports_profile = relationship("SportsProfile", back_populates="user", uselist=False)
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    business_profile = relationship("BusinessProfile", back_populates="user", uselist=False)
    payout_requests = relationship("PayoutRequest", back_populates="user", foreign_keys="PayoutRequest.user_id")
    verification_requests = relationship("VerificationRequest", back_populates="user", foreign_keys="VerificationRequest.user_id")
    bookings = relationship("Booking", back_populates="user")


class OrganizerProfile(Base):
    __tablename__ = "organizer_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Organization Info
    organization_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(Enum(City), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    is_business = Column(Boolean, default=False)
    verification_documents = Column(JSON, nullable=True)
    
    # Stats
    events_count = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Link to unified BusinessProfile
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="organizer_profile")
    events = relationship("Event", back_populates="organizer")
    business_profile = relationship("BusinessProfile", back_populates="organizer_profiles")
    followers = relationship("OrganizerFollow", back_populates="organizer")


class VenueProfile(Base):
    __tablename__ = "venue_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Venue Info
    venue_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    venue_type = Column(String(50), nullable=True)  # Club, Beach, Hall, Lounge, Restaurant
    
    # Location
    city = Column(Enum(City), nullable=False)
    address = Column(String(500), nullable=False)
    landmark = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Contact
    phone = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    
    # Media
    photos = Column(JSON, nullable=True)  # Array of photo URLs
    cover_photo = Column(String(500), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    business_registration_number = Column(String(100), nullable=True)
    business_certificate_url = Column(String(500), nullable=True)
    owner_id_url = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected, active
    
    # Stats
    total_events = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="venue_profile")
    subscriptions = relationship("VenueSubscription", back_populates="venue")


class SportsProfile(Base):
    """Sports facility owner profile - similar to venue but optimized for sports"""
    __tablename__ = "sports_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Relationships
    user = relationship("User", back_populates="sports_profile")
    courts = relationship("SportsCourt", back_populates="facility")
    bookings = relationship("SportsBooking", back_populates="facility")
    subscriptions = relationship("SportsSubscription", back_populates="sports")


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Basic placeholders for compatibility
    name = Column(String(200), nullable=True)

    # Relationship
    user = relationship("User")

    # Facility Info
    facility_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    facility_types = Column(JSON, nullable=True)  # Football, Basketball, Tennis, etc.
    
    # Location
    city = Column(Enum(City), nullable=False)
    address = Column(String(500), nullable=False)
    landmark = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Contact
    phone = Column(String(20), nullable=True)
    whatsapp = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Media
    photos = Column(JSON, nullable=True)
    cover_photo = Column(String(500), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    business_registration_number = Column(String(100), nullable=True)
    
    # Operating hours
    opening_time = Column(String(5), nullable=True)  # 06:00
    closing_time = Column(String(5), nullable=True)  # 23:00
    
    # Status
    status = Column(String(50), default="pending")
    
    # Stats
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    occupancy_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    followers = relationship("VendorFollow", back_populates="vendor")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Business Info
    business_name = Column(String(200), nullable=False)
    business_type = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_documents = Column(JSON, nullable=True)
    
    # Stats
    total_revenue = Column(Float, default=0.0)
    events_count = Column(Integer, default=0)
    
    # Location
    city = Column(Enum(City), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="business_profile")
    organizer_profiles = relationship("OrganizerProfile", back_populates="business_profile")
    clubs = relationship("Club", back_populates="business_claimed_by")
    food_spots = relationship("FoodSpot", back_populates="business_claimed_by")


class AdminUser(Base):
    """Admin dashboard users with role-based access"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Role & Permissions
    role = Column(Enum(AdminRole), default=AdminRole.SUPPORT_ADMIN)
    
    # Status
    status = Column(String(50), default="active")  # active, inactive, suspended
    
    # Audit
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    activity_logs = relationship("AdminActivityLog", back_populates="admin")


class SystemConfig(Base):
    """Dynamic system configuration (no-code settings)"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    category = Column(String(50), nullable=True)  # revenue, subscription, feature_toggles, display, local
    description = Column(Text, nullable=True)
    
    updated_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    updated_by = relationship("AdminUser")


class AdminActivityLog(Base):
    """Audit trail for all admin actions"""
    __tablename__ = "admin_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    
    action = Column(String(100), nullable=False)  # create, update, delete, approve, reject, login
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("AdminUser", back_populates="activity_logs")


class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    
    # Location
    city = Column(Enum(City), nullable=False)
    address = Column(String(500), nullable=False)
    district = Column(String(100), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Music & Vibe
    music_genres = Column(JSON, nullable=True)
    is_afrobeat_friendly = Column(Boolean, default=False)
    
    # Images
    cover_image = Column(String(500), nullable=True)
    gallery_images = Column(JSON, nullable=True)
    
    # Contact
    phone = Column(String(20), nullable=True)
    
    # Status
    is_verified = Column(Boolean, default=False)
    
    # Business claim
    business_claimed_by_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business_claimed_by = relationship("BusinessProfile", back_populates="clubs")


class FoodSpot(Base):
    __tablename__ = "food_spots"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(200), nullable=False)
    
    # Location
    city = Column(Enum(City), nullable=False)
    address = Column(String(500), nullable=False)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Food details
    cuisine_type = Column(String(100), nullable=True)
    price_range = Column(String(10), nullable=True)
    
    # Images
    cover_image = Column(String(500), nullable=True)
    
    # Status
    is_verified = Column(Boolean, default=False)
    
    # Business claim
    business_claimed_by_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business_claimed_by = relationship("BusinessProfile", back_populates="food_spots")


class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    
    # Location
    address = Column(String(500), nullable=False)
    city = Column(Enum(City), nullable=False)
    district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Details
    description = Column(Text, nullable=True)
    capacity = Column(Integer, nullable=True)
    
    # Contact
    phone = Column(String(20), nullable=True)
    
    # Images
    images = Column(JSON, nullable=True)
    cover_image = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="venue")


class SportsCourt(Base):
    """Individual court/pitch at a sports facility"""
    __tablename__ = "sports_courts"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("sports_profiles.id"), nullable=False)
    
    # Court Info
    name = Column(String(100), nullable=False)  # Pitch A, Court B
    sport_type = Column(String(50), nullable=False)  # football_5a, basketball, tennis, etc.
    surface_type = Column(String(50), nullable=False)  # grass, astroturf, concrete, wood
    capacity = Column(Integer, nullable=True)
    
    # Amenities
    has_floodlights = Column(Boolean, default=False)
    has_changing_rooms = Column(Boolean, default=False)
    has_showers = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_seating = Column(Boolean, default=False)
    has_scoreboard = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    facility = relationship("SportsProfile", back_populates="courts")
    bookings = relationship("SportsBooking", back_populates="court")
    pricing_rules = relationship("SportsPricingRule", back_populates="court")


class SportsBooking(Base):
    """Hourly/daily sports facility booking"""
    __tablename__ = "sports_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("sports_profiles.id"), nullable=False, index=True)
    court_id = Column(Integer, ForeignKey("sports_courts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Booking info
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)
    
    # Time
    booking_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(String(5), nullable=False)  # 18:00
    end_time = Column(String(5), nullable=False)    # 20:00
    duration_hours = Column(Integer, nullable=False)
    
    # Team/Group info
    team_name = Column(String(100), nullable=True)
    num_players = Column(Integer, nullable=True)
    
    # Payment
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="SLE")
    payment_status = Column(String(50), default="pending")  # pending, completed, refunded
    payment_id = Column(String(255), nullable=True)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    checked_in = Column(Boolean, default=False)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    facility = relationship("SportsProfile", back_populates="bookings")
    court = relationship("SportsCourt", back_populates="bookings")
    user = relationship("User")


class Booking(Base):
    """Venue booking/reservation"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Booking details
    booking_date = Column(DateTime(timezone=True), nullable=False)
    duration = Column(String(50), nullable=True)
    
    # Payment
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="SLE")
    payment_status = Column(String(50), default="pending")
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    venue = relationship("Venue")
    user = relationship("User", back_populates="bookings")


class SubscriptionTier(Base):
    """Subscription tiers for venue/organizers (Basic, Spotlight, Premier, Enterprise)"""
    __tablename__ = "subscription_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    tier_code = Column(String(50), unique=True, nullable=False)  # basic, spotlight, premier, enterprise
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing in SLE (Leones)
    weekly_price_sle = Column(Integer, nullable=True)
    monthly_price_sle = Column(Integer, nullable=True)
    yearly_price_sle = Column(Integer, nullable=True)
    
    # Features JSON
    features = Column(JSON, nullable=False, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    venue_subscriptions = relationship("VenueSubscription", back_populates="tier")
    organizer_subscriptions = relationship("OrganizerSubscription", back_populates="tier")
    sports_subscriptions = relationship("SportsSubscription", back_populates="tier")


class VenueSubscription(Base):
    """Active subscription for a venue"""
    __tablename__ = "venue_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venue_profiles.id"), nullable=False, index=True)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False, index=True)
    
    # Status
    status = Column(String(50), default="active")  # active, expired, cancelled
    
    # Dates
    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=True)
    
    # Payment method
    payment_method = Column(String(50), nullable=True)  # orange_money, africell_money, bank_transfer
    
    # Last transaction
    last_payment_id = Column(String(255), nullable=True)
    last_paid_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    venue = relationship("VenueProfile", back_populates="subscriptions")
    tier = relationship("SubscriptionTier", back_populates="venue_subscriptions")


class OrganizerSubscription(Base):
    """Active subscription for an organizer (Pro features)"""
    __tablename__ = "organizer_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    
    # Status
    status = Column(String(50), default="active")
    
    # Dates
    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organizer = relationship("OrganizerProfile")
    tier = relationship("SubscriptionTier", back_populates="organizer_subscriptions")


class SportsSubscription(Base):
    """Active subscription for a sports facility"""
    __tablename__ = "sports_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    sports_id = Column(Integer, ForeignKey("sports_profiles.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    
    # Status
    status = Column(String(50), default="active")
    
    # Dates
    started_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sports = relationship("SportsProfile", back_populates="subscriptions")
    tier = relationship("SubscriptionTier", back_populates="sports_subscriptions")


class SportsPricingRule(Base):
    """Dynamic pricing for sports courts by time slot"""
    __tablename__ = "sports_pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("sports_courts.id"), nullable=False)
    
    # Time period
    day_of_week = Column(String(10), nullable=False)  # monday, tuesday, etc. or 'weekday', 'weekend'
    start_time = Column(String(5), nullable=False)  # 06:00
    end_time = Column(String(5), nullable=False)    # 18:00
    
    # Pricing
    hourly_rate_sle = Column(Integer, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    court = relationship("SportsCourt", back_populates="pricing_rules")


# REMOVED: VendorProfile, Product, EventVendor, BookingRequest, BookingMessage, ArtistReview, ArtistAvailability, ArtistTrack

class PayoutRequest(Base):
    __tablename__ = "payout_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User requesting payout
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="SLE")
    
    # Status
    status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING)
    
    # Payment method and details
    payment_method = Column(String(50), nullable=True)
    payment_details = Column(JSON, nullable=True)
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processed by
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payout_requests", foreign_keys=[user_id])
    processed_by = relationship("User", foreign_keys=[processed_by_id])


class VerificationRequest(Base):
    __tablename__ = "verification_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User requesting verification
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Request type
    request_type = Column(Enum(VerificationType), nullable=False)
    
    # Status
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    
    # Documents
    documents = Column(JSON, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processed by
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Admin notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="verification_requests", foreign_keys=[user_id])
    processed_by = relationship("User", foreign_keys=[processed_by_id])


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    
    # Event Info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Date & Time
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Location
    city = Column(Enum(City), nullable=False)
    address = Column(String(500), nullable=True)
    
    # Media
    flyer_image = Column(String(500), nullable=True)
    gallery_images = Column(JSON, nullable=True)
    
    # Capacity & Status
    capacity = Column(Integer, nullable=True)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    
    # Stats
    views_count = Column(Integer, default=0)
    tickets_sold = Column(Integer, default=0)
    
    # Social sharing
    share_url = Column(String(500), nullable=True)
    qr_code = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organizer = relationship("OrganizerProfile", back_populates="events")
    venue = relationship("Venue", back_populates="events")
    ticket_tiers = relationship("TicketTier", back_populates="event")
    followers = relationship("EventFollow", back_populates="event")
    tickets = relationship("Ticket", back_populates="event")


class TicketTier(Base):
    __tablename__ = "ticket_tiers"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Ticket Tier Info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="SLE")
    
    quantity = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, default=0)
    
    # Limits
    max_per_order = Column(Integer, default=10)
    
    # Status
    status = Column(Enum(TicketStatus), default=TicketStatus.AVAILABLE)
    
    # Sale period
    sale_start = Column(DateTime(timezone=True), nullable=True)
    sale_end = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="ticket_tiers")
    tickets = relationship("Ticket", back_populates="ticket_tier")


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    ticket_tier_id = Column(Integer, ForeignKey("ticket_tiers.id"), index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    
    # Ticket Info
    ticket_number = Column(String(50), unique=True, nullable=False)
    qr_token = Column(String(255), unique=True, index=True, nullable=False)
    qr_code = Column(String(1500), nullable=True)
    
    # Status
    status = Column(String(50), default="active", index=True)
    
    # Verification
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Audit trail
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    ticket_tier = relationship("TicketTier", back_populates="tickets")
    order = relationship("Order", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    verified_by_user = relationship("User", foreign_keys=[verified_by_user_id])


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Order Info
    order_number = Column(String(50), unique=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="SLE")
    
    # Payment
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_id = Column(String(255), nullable=True)
    payment_phone = Column(String(20), nullable=True)  # Mobile money phone number
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Refund
    refund_amount = Column(Float, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Idempotency (prevent duplicate payments)
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    tickets = relationship("Ticket", back_populates="order")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    ticket_tier_id = Column(Integer, ForeignKey("ticket_tiers.id"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    ticket_tier = relationship("TicketTier")


class PaymentVerification(Base):
    """Stores payment screenshot uploads for manual/auto verification"""
    __tablename__ = "payment_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_ref = Column(String(50), nullable=False, index=True)
    
    # Screenshot image
    screenshot_url = Column(String(500), nullable=True)
    
    # Detected information
    detected_amount = Column(Float, nullable=True)
    detected_date = Column(String(50), nullable=True)
    detected_time = Column(String(50), nullable=True)
    detected_payee = Column(String(200), nullable=True)
    
    # Verification status
    status = Column(String(20), default="pending")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Rejection reason
    rejection_reason = Column(Text, nullable=True)
    
    # Expected payment amount
    expected_amount = Column(Float, nullable=False)
    
    # External payment reference
    payment_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Deleted YooPayPayment


class ArtistFollow(Base):
    __tablename__ = "artist_follows"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    artist_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class EventFollow(Base):
    __tablename__ = "event_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_event_follow_user_event'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    event = relationship("Event", back_populates="followers")


class OTPCode(Base):
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    otp_type = Column(String(10), nullable=False, default="sms")
    purpose = Column(String(50), nullable=True, default="login")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VendorFollow(Base):
    __tablename__ = "vendor_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'vendor_id', name='uq_vendor_follow_user'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    vendor = relationship("VendorProfile", back_populates="followers")


class OrganizerFollow(Base):
    __tablename__ = "organizer_follows"
    __table_args__ = (
        UniqueConstraint('user_id', 'organizer_id', name='uq_organizer_follow_user'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    organizer = relationship("OrganizerProfile", back_populates="followers")


class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeaturedItem(Base):
    __tablename__ = "featured_items"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    position = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="general")
    
    # Link to related entity
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ═══════════════════════════════════════════════════════════════════════════
# RECAPS - Event Photo Highlights Feature
# ═══════════════════════════════════════════════════════════════════════════

class Recap(Base):
    """
    Recaps - Event Photo Highlights
    Businesses/Organizers can post photos from past events (max 20 photos)
    to showcase the experience for users
    """
    __tablename__ = "recaps"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to the event
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id"), nullable=False)
    
    # Recap Info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Photos (max 20)
    photos = Column(JSON, nullable=False, default=list)  # Array of photo URLs
    
    # Stats
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    
    # Status
    status = Column(Enum(RecapStatus), default=RecapStatus.DRAFT)
    
    # Publishing
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event")
    organizer = relationship("OrganizerProfile")
    likes = relationship("RecapLike", back_populates="recap")


class RecapLike(Base):
    """User likes on recaps"""
    __tablename__ = "recap_likes"
    __table_args__ = (
        UniqueConstraint('recap_id', 'user_id', name='uq_recap_like_user'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    recap_id = Column(Integer, ForeignKey("recaps.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recap = relationship("Recap", back_populates="likes")
    
# ═══════════════════════════════════════════════════════════════════════════
# SIERRA LEONE FEATURES - Sports, Deals, Crews
# ═══════════════════════════════════════════════════════════════════════════

class Sport(Base):
    """Matches, viewing centers, and community sports events"""
    __tablename__ = "sports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False) # Match, Viewing Center, Community Event
    
    city = Column(Enum(City), nullable=False)
    location = Column(String(500), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Deal(Base):
    """Discounts, offers, and promotions from vendors/venues"""
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    discount_code = Column(String(50), nullable=True)
    
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="active")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Crew(Base):
    """Groups, promoters, and organizers"""
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    
    organizer_id = Column(Integer, ForeignKey("organizer_profiles.id"), nullable=False)
    
    members_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organizer = relationship("OrganizerProfile")

# Unique constraint override for RecapLike
RecapLike.__table_args__ = (
    {'sqlite_autoincrement': True},
)


# ═══════════════════════════════════════════════════════════════════════════
# SPORTS MATCH TICKETING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class SportsLeague(Base):
    """Sports league (Premier League, Basketball League, etc.)"""
    __tablename__ = "sports_leagues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    short_name = Column(String(50), nullable=True)
    sport_type = Column(String(50), nullable=False)  # football, basketball, tennis, volleyball
    season = Column(String(20), nullable=False)  # "2024/25", "2025"
    logo_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    
    # Organizer
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Status
    status = Column(Enum(LeagueStatus), default=LeagueStatus.ACTIVE)
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Featured on platform
    featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organizer = relationship("User")
    teams = relationship("Team", back_populates="league")
    fixtures = relationship("Fixture", back_populates="league")
    standings = relationship("LeagueStanding", back_populates="league")


class Team(Base):
    """Sports team"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(10), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Location
    city = Column(String(100), nullable=False)
    
    # League
    league_id = Column(Integer, ForeignKey("sports_leagues.id"), nullable=False)
    
    # Home venue (if applicable)
    home_venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    home_facility_id = Column(Integer, ForeignKey("sports_profiles.id"), nullable=True)
    
    # Team info
    founded_year = Column(Integer, nullable=True)
    colors = Column(JSON, nullable=True)  # {primary: "#C7F600", secondary: "#000000"}
    description = Column(Text, nullable=True)
    social_links = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="active")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    league = relationship("SportsLeague", back_populates="teams")
    home_venue = relationship("Venue")
    home_facility = relationship("SportsProfile")
    home_fixtures = relationship("Fixture", foreign_keys="Fixture.home_team_id", back_populates="home_team")
    away_fixtures = relationship("Fixture", foreign_keys="Fixture.away_team_id", back_populates="away_team")
    standings = relationship("LeagueStanding", back_populates="team")
    followers = relationship("UserFavoriteTeam", back_populates="team")


class Fixture(Base):
    """Sports match/fixture"""
    __tablename__ = "fixtures"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # League and teams
    league_id = Column(Integer, ForeignKey("sports_leagues.id"), nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Venue
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    facility_id = Column(Integer, ForeignKey("sports_profiles.id"), nullable=True)
    
    # Match details
    match_date = Column(DateTime(timezone=True), nullable=False)
    match_type = Column(String(50), default="league")  # league, cup, friendly, playoff
    matchday = Column(Integer, nullable=True)  # Week/round number
    
    # Scores
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    home_ht_score = Column(Integer, nullable=True)  # Half-time
    away_ht_score = Column(Integer, nullable=True)
    
    # Status
    status = Column(Enum(FixtureStatus), default=FixtureStatus.SCHEDULED)
    
    # Ticketing integration
    is_ticketed = Column(Boolean, default=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)  # Links to events for tickets
    ticket_sale_starts = Column(DateTime(timezone=True), nullable=True)
    ticket_sale_ends = Column(DateTime(timezone=True), nullable=True)
    
    # Match metadata
    attendance = Column(Integer, nullable=True)
    highlights_video_url = Column(String(500), nullable=True)
    
    # Audit
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    league = relationship("SportsLeague", back_populates="fixtures")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_fixtures")
    venue = relationship("Venue")
    facility = relationship("SportsProfile")
    event = relationship("Event")
    created_by = relationship("User")
    events = relationship("FixtureEvent", back_populates="fixture")


class FixtureEvent(Base):
    """Events during a match (goals, cards, subs)"""
    __tablename__ = "fixture_events"
    
    id = Column(Integer, primary_key=True, index=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable=False)
    
    # Event details
    event_type = Column(Enum(MatchEventType), nullable=False)
    minute = Column(Integer, nullable=False)
    
    # Team and player
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_name = Column(String(255), nullable=False)  # Store name since we may not have full player DB yet
    
    # Secondary player (assist, substituted player)
    secondary_player_name = Column(String(255), nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fixture = relationship("Fixture", back_populates="events")
    team = relationship("Team")


class LeagueStanding(Base):
    """League table standings (auto-calculated)"""
    __tablename__ = "league_standings"
    
    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("sports_leagues.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Position
    position = Column(Integer, nullable=False)
    
    # Match stats
    played = Column(Integer, default=0)
    won = Column(Integer, default=0)
    drawn = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    goal_difference = Column(Integer, default=0)
    points = Column(Integer, default=0)
    
    # Form (last 5 results: "WWDLW")
    form = Column(String(10), nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    league = relationship("SportsLeague", back_populates="standings")
    team = relationship("Team", back_populates="standings")


class UserFavoriteTeam(Base):
    """User following a team"""
    __tablename__ = "user_favorite_teams"
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_user_favorite_team'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    
    # Notification preference
    notify_matches = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    team = relationship("Team", back_populates="followers")


class ContactSubmission(Base):
    """Contact form submissions stored in database"""
    __tablename__ = "contact_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    phone = Column(String(20), nullable=True)
    status = Column(String(50), default="open")
    replied_at = Column(DateTime(timezone=True), nullable=True)
    replied_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
