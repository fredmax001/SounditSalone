from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class VenueManager(Base):
    __tablename__ = "venue_managers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    reservation_code = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)

    reservation_date = Column(DateTime(timezone=True), nullable=False)
    reservation_time = Column(String(32), nullable=True)
    party_size = Column(Integer, default=1)
    table_number = Column(String(32), nullable=True)
    status = Column(String(20), default="pending", index=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SportsFacility(Base):
    __tablename__ = "sports_facilities"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    facility_type = Column(String(100), nullable=True)

    city = Column(String(100), nullable=True, index=True)
    area = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    landmark = Column(String(255), nullable=True)

    operating_hours = Column(JSON, nullable=True)
    booking_rules = Column(JSON, nullable=True)
    amenities = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SportsCalendarBlock(Base):
    __tablename__ = "sports_calendar_blocks"

    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("sports_courts.id"), nullable=False, index=True)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(255), nullable=True)

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SportsTeam(Base):
    __tablename__ = "sports_teams"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("sports_facilities.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    captain_name = Column(String(200), nullable=True)
    captain_phone = Column(String(32), nullable=True)
    captain_email = Column(String(255), nullable=True)
    players_count = Column(Integer, default=0)

    preferred_court_id = Column(Integer, ForeignKey("sports_courts.id"), nullable=True)
    discount_rate = Column(Float, default=0)
    total_bookings = Column(Integer, default=0)
    total_revenue = Column(Float, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdminRole(Base):
    __tablename__ = "admin_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    role_type = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    is_system_role = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdminUserRole(Base):
    __tablename__ = "admin_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey("admin_roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    previous_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeaturedEvent(Base):
    __tablename__ = "featured_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DisabledEvent(Base):
    __tablename__ = "disabled_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, unique=True, index=True)
    reason = Column(Text, nullable=True)
    disabled_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    disabled_at = Column(DateTime(timezone=True), server_default=func.now())


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    target_role = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False, default=0)
    currency = Column(String(3), default="SLL")
    billing_cycle = Column(String(20), default="monthly")
    commission_rate = Column(Float, default=0.04)
    features = Column(JSON, nullable=True)
    limits = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True)
    status = Column(String(20), default="active", index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50), nullable=True)
    transaction_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(32), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    subject = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="general")
    priority = Column(String(20), nullable=False, default="medium")
    status = Column(String(30), nullable=False, default="open", index=True)
    description = Column(Text, nullable=True)

    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupportTicketReply(Base):
    __tablename__ = "support_ticket_replies"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
