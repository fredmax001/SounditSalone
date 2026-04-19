"""
Sound It Platform - Production Database Configuration
======================================================
Optimized database configuration with:
- Connection pooling
- Query optimization
- Index management
- Health monitoring
"""

import logging
from typing import Generator
from sqlalchemy import create_engine, event, text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from config_production import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Base class for models
Base = declarative_base()

# Configure engine based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (development only)
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
    logger.warning("Using SQLite - NOT RECOMMENDED FOR PRODUCTION")
else:
    # PostgreSQL configuration (production)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.DEBUG,
    )
    logger.info(f"PostgreSQL connection pool initialized: size={settings.DB_POOL_SIZE}")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Performance monitoring
@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries"""
    context._query_start_time = __import__('time').time()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time"""
    total_time = __import__('time').time() - context._query_start_time
    if total_time > 1.0:  # Log queries taking more than 1 second
        logger.warning(f"Slow query ({total_time:.2f}s): {statement[:200]}...")


def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions (for non-FastAPI usage)"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_health() -> dict:
    """Check database health and return status"""
    try:
        with engine.connect() as conn:
            # Check connection
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get connection pool stats (PostgreSQL only)
            if not settings.DATABASE_URL.startswith("sqlite"):
                stats = {
                    "size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                }
            else:
                stats = {}
            
            return {
                "status": "healthy",
                "connected": True,
                "pool_stats": stats
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }


def create_performance_indexes():
    """Create database indexes for performance optimization"""
    
    indexes = [
        # User indexes
        Index('idx_users_email', 'users.email'),
        Index('idx_users_phone', 'users.phone'),
        Index('idx_users_role', 'users.role'),
        Index('idx_users_status', 'users.status'),
        Index('idx_users_created_at', 'users.created_at'),
        
        # Event indexes
        Index('idx_events_organizer_id', 'events.organizer_id'),
        Index('idx_events_city', 'events.city'),
        Index('idx_events_status', 'events.status'),
        Index('idx_events_start_date', 'events.start_date'),
        Index('idx_events_city_status', 'events.city', 'events.status'),
        
        # Ticket indexes
        Index('idx_tickets_user_id', 'tickets.user_id'),
        Index('idx_tickets_ticket_tier_id', 'tickets.ticket_tier_id'),
        Index('idx_tickets_order_id', 'tickets.order_id'),
        Index('idx_tickets_ticket_number', 'tickets.ticket_number'),
        Index('idx_tickets_is_used', 'tickets.is_used'),
        
        # Ticket tier indexes
        Index('idx_ticket_tiers_event_id', 'ticket_tiers.event_id'),
        Index('idx_ticket_tiers_status', 'ticket_tiers.status'),
        
        # Order indexes
        Index('idx_orders_user_id', 'orders.user_id'),
        Index('idx_orders_order_number', 'orders.order_number'),
        Index('idx_orders_payment_status', 'orders.payment_status'),
        Index('idx_orders_created_at', 'orders.created_at'),
        
        # Order item indexes
        Index('idx_order_items_order_id', 'order_items.order_id'),
        Index('idx_order_items_ticket_tier_id', 'order_items.ticket_tier_id'),
        
        # Venue indexes
        Index('idx_venue_profiles_user_id', 'venue_profiles.user_id'),
        Index('idx_venue_profiles_city', 'venue_profiles.city'),
        Index('idx_venue_profiles_is_verified', 'venue_profiles.is_verified'),
        
        # Organizer indexes
        Index('idx_organizer_profiles_user_id', 'organizer_profiles.user_id'),
        Index('idx_organizer_profiles_city', 'organizer_profiles.city'),
        Index('idx_organizer_profiles_is_verified', 'organizer_profiles.is_verified'),
        
        # Booking indexes
        Index('idx_bookings_venue_id', 'bookings.venue_id'),
        Index('idx_bookings_user_id', 'bookings.user_id'),
        Index('idx_bookings_status', 'bookings.status'),
        
        # OTP indexes
        Index('idx_otp_codes_identifier', 'otp_codes.identifier'),
        Index('idx_otp_codes_expires_at', 'otp_codes.expires_at'),
        Index('idx_otp_codes_is_used', 'otp_codes.is_used'),
        
        # Payment verification indexes
        Index('idx_payment_verifications_order_ref', 'payment_verifications.order_ref'),
        Index('idx_payment_verifications_status', 'payment_verifications.status'),
        
        # Social indexes
        Index('idx_organizer_follows_user_id', 'organizer_follows.user_id'),
        Index('idx_organizer_follows_organizer_id', 'organizer_follows.organizer_id'),
        Index('idx_event_follows_user_id', 'event_follows.user_id'),
        Index('idx_event_follows_event_id', 'event_follows.event_id'),
        
        # Notification indexes
        Index('idx_notifications_user_id', 'notifications.user_id'),
        Index('idx_notifications_is_read', 'notifications.is_read'),
        Index('idx_notifications_created_at', 'notifications.created_at'),
    ]
    
    return indexes


def init_db():
    """Initialize database tables and indexes"""
    # Import all models to ensure they're registered with Base
    from models import (
        User, OTPCode, Event, Club, FoodSpot, Order, OrderItem,
        ArtistProfile, DJMix, OrganizerProfile, BusinessProfile,
        BookingRequest, BookingMessage, ArtistReview, ArtistAvailability, ArtistTrack,
        PayoutRequest, VerificationRequest, Venue,
        EventArtist, TicketTier, Ticket,
        ArtistFollow, EventFollow, VendorFollow, OrganizerFollow,
        Notification, VendorProfile, Product, EventVendor,
        SearchLog, FeaturedItem, PaymentVerification
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Create performance indexes
    # Note: In production, use Alembic migrations for index management
    indexes = create_performance_indexes()
    logger.info(f"Performance indexes defined: {len(indexes)}")


def cleanup_old_data(db: Session, days: int = 90):
    """Clean up old data (expired OTPs, old logs, etc.)"""
    from datetime import datetime, timedelta
    from models import OTPCode, SearchLog, Notification
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Delete old used OTPs
    old_otps = db.query(OTPCode).filter(
        OTPCode.is_used == True,
        OTPCode.created_at < cutoff_date
    ).delete(synchronize_session=False)
    
    # Delete old search logs
    old_searches = db.query(SearchLog).filter(
        SearchLog.created_at < cutoff_date
    ).delete(synchronize_session=False)
    
    # Delete old read notifications
    old_notifications = db.query(Notification).filter(
        Notification.is_read == True,
        Notification.created_at < cutoff_date
    ).delete(synchronize_session=False)
    
    db.commit()
    
    logger.info(f"Cleaned up: {old_otps} OTPs, {old_searches} searches, {old_notifications} notifications")
    
    return {
        "otps_deleted": old_otps,
        "searches_deleted": old_searches,
        "notifications_deleted": old_notifications
    }


def get_database_stats(db: Session) -> dict:
    """Get database statistics for monitoring"""
    from sqlalchemy import func
    from models import (
        User, Event, Order, Ticket, VenueProfile, 
        OrganizerProfile, SportsProfile, Booking
    )
    
    return {
        "users": {
            "total": db.query(User).count(),
            "active": db.query(User).filter(User.status == "active").count(),
            "organizers": db.query(OrganizerProfile).count(),
            "venues": db.query(VenueProfile).count(),
            "sports_facilities": db.query(SportsProfile).count(),
        },
        "events": {
            "total": db.query(Event).count(),
            "upcoming": db.query(Event).filter(Event.start_date > func.now()).count(),
        },
        "orders": {
            "total": db.query(Order).count(),
            "completed": db.query(Order).filter(Order.payment_status == "completed").count(),
            "pending": db.query(Order).filter(Order.payment_status == "pending").count(),
        },
        "tickets": {
            "total": db.query(Ticket).count(),
            "used": db.query(Ticket).filter(Ticket.is_used == True).count(),
        },
        "bookings": {
            "total": db.query(Booking).count(),
            "pending": db.query(Booking).filter(Booking.status == "pending").count(),
            "accepted": db.query(Booking).filter(Booking.status == "accepted").count(),
        }
    }
