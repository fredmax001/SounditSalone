from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import get_settings

settings = get_settings()

# Configure engine based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for local development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CustomBase:
    __table_args__ = {'extend_existing': True}

Base = declarative_base(cls=CustomBase)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered with Base
    from models import (
        User, OrganizerProfile, VenueProfile, SportsProfile, BusinessProfile,
        AdminUser, SystemConfig, AdminActivityLog, Club, FoodSpot, Venue,
        SportsBooking, Booking, SubscriptionTier, VenueSubscription,
        OrganizerSubscription, SportsSubscription, SportsPricingRule,
        PayoutRequest, VerificationRequest, Event,
        TicketTier, Ticket, Order, OrderItem, PaymentVerification,
        EventFollow, OTPCode, OrganizerFollow,
        Notification, Recap, RecapLike,
        SportsLeague, Team, Fixture, FixtureEvent, LeagueStanding, UserFavoriteTeam
    )
    from models_platform import (
        VenueManager, Reservation,
        SportsFacility, SportsCalendarBlock, SportsTeam,
        AdminRole, UserActivityLog,
        FeaturedEvent, DisabledEvent,
        SubscriptionPlan, UserSubscription,
        SupportTicket, SupportTicketReply,
    )
    
    # Use checkfirst=True to skip tables that already exist
    # This prevents errors when running on an existing database
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"Note during table creation: {e}")
        # If create_all fails, try creating tables individually
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table_name in Base.metadata.tables:
            if table_name not in existing_tables:
                try:
                    table = Base.metadata.tables[table_name]
                    table.create(engine, checkfirst=True)
                    print(f"Created table: {table_name}")
                except Exception as te:
                    print(f"Could not create table {table_name}: {te}")
    
    _seed_platform_defaults()


def _seed_platform_defaults() -> None:
    """Seed core Sierra Leone platform defaults for roles, config, and plans."""
    from models_platform import AdminRole, SubscriptionPlan
    from models import SystemConfig

    db = SessionLocal()
    try:
        # Check if seeding is even needed
        existing_roles = db.query(AdminRole).count()
        if existing_roles > 0:
            print(f"Database already seeded with {existing_roles} roles, skipping seeding")
            return
        default_roles = [
            {
                "name": "Super Admin",
                "role_type": "super_admin",
                "description": "Full platform control",
                "permissions": ["*"],
            },
            {
                "name": "Finance Admin",
                "role_type": "finance_admin",
                "description": "Transactions, payouts, and commission control",
                "permissions": ["finance.read", "finance.write", "payouts.manage"],
            },
            {
                "name": "Marketing Admin",
                "role_type": "marketing_admin",
                "description": "Promotions, campaigns, and featured placement",
                "permissions": ["marketing.read", "marketing.write", "featured.manage"],
            },
            {
                "name": "Maintenance Admin",
                "role_type": "maintenance_admin",
                "description": "System health, logs, and platform maintenance",
                "permissions": ["system.read", "system.maintenance", "logs.read"],
            },
            {
                "name": "Support Admin",
                "role_type": "support_admin",
                "description": "Support ticket and user issue resolution",
                "permissions": ["support.read", "support.write", "users.lookup"],
            },
        ]

        for role_data in default_roles:
            role = db.query(AdminRole).filter(AdminRole.role_type == role_data["role_type"]).first()
            if not role:
                db.add(AdminRole(**role_data))
            else:
                role.name = role_data["name"]
                role.description = role_data["description"]
                role.permissions = role_data["permissions"]
                role.is_active = True
                role.is_system_role = True

        default_config = [
            ("country", {"value": "Sierra Leone"}, "local", "Primary operating country"),
            ("currency_code", {"value": "SLL"}, "local", "Primary platform currency"),
            ("currency_symbol", {"value": "Le"}, "local", "Currency symbol"),
            ("secondary_currency_code", {"value": "USD"}, "local", "Optional display currency"),
            ("timezone", {"value": "Africa/Freetown"}, "local", "Primary platform timezone"),
            ("default_commission_rate", {"value": 0.04}, "revenue", "Default commission rate"),
            ("minimum_payout_sll", {"value": 50000}, "revenue", "Minimum payout in SLL"),
        ]

        for key, value, category, description in default_config:
            config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
            if not config:
                db.add(
                    SystemConfig(
                        config_key=key,
                        config_value=value,
                        category=category,
                        description=description,
                    )
                )
            else:
                config.config_value = value
                config.category = category
                config.description = description

        default_plans = [
            {
                "name": "Organizer Pro Monthly",
                "slug": "organizer-pro-monthly",
                "description": "Organizer pro features with reduced commission",
                "target_role": "organizer",
                "price": 500,
                "currency": "SLL",
                "billing_cycle": "monthly",
                "commission_rate": 0.04,
                "features": ["Unlimited events", "Advanced analytics", "Promo tools"],
                "limits": {"events_per_month": -1},
                "is_active": True,
                "is_featured": True,
            },
            {
                "name": "Venue Spotlight Monthly",
                "slug": "venue-spotlight-monthly",
                "description": "Venue visibility and analytics upgrade",
                "target_role": "venue",
                "price": 1000,
                "currency": "SLL",
                "billing_cycle": "monthly",
                "commission_rate": 0.04,
                "features": ["Homepage feature", "Search boost", "Analytics"],
                "limits": {"events_per_month": 10},
                "is_active": True,
                "is_featured": True,
            },
            {
                "name": "Sports Spotlight Monthly",
                "slug": "sports-spotlight-monthly",
                "description": "Sports facility listing boost and lower commission",
                "target_role": "sport",
                "price": 800,
                "currency": "SLL",
                "billing_cycle": "monthly",
                "commission_rate": 0.04,
                "features": ["Featured placement", "Advanced analytics"],
                "limits": {"courts_listed": -1},
                "is_active": True,
                "is_featured": True,
            },
        ]

        for plan_data in default_plans:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.slug == plan_data["slug"]).first()
            if not plan:
                db.add(SubscriptionPlan(**plan_data))
            else:
                for key, value in plan_data.items():
                    setattr(plan, key, value)

        db.commit()
    finally:
        db.close()
