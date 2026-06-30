import logging
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
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
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
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


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions with automatic rollback on error.

    Useful for background tasks, scripts, and any non-FastAPI code path that
    needs explicit transaction control.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_health() -> dict:
    """Check database connectivity and return status + pool stats."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).fetchone()

        stats = {}
        if not settings.DATABASE_URL.startswith("sqlite"):
            stats = {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
            }

        return {
            "status": "healthy",
            "connected": True,
            "pool_stats": stats,
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
        }


def init_db():
    """Initialize database state.

    For SQLite (local development), tables are created automatically from the
    model metadata. For PostgreSQL, the application relies on Alembic
    migrations; if tables are missing we create them as a fallback but log a
    warning so operators know to run ``alembic upgrade head`` in production.
    """
    # Import all model modules to register classes with Base.metadata
    import models  # noqa: F401
    import models_platform  # noqa: F401
    from sqlalchemy import inspect

    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if is_sqlite:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    elif not existing_tables:
        print(
            "WARNING: PostgreSQL database has no tables. Creating schema from "
            "models as a fallback. For production, run 'alembic upgrade head' "
            "before starting the application."
        )
        Base.metadata.create_all(bind=engine, checkfirst=True)
    else:
        print(f"Database already has {len(existing_tables)} tables; skipping create_all. "
              "Ensure Alembic migrations are up to date.")

    _seed_platform_defaults()
    create_performance_indexes()


def create_performance_indexes() -> None:
    """Create critical performance indexes that are missing from the models.

    These indexes target the most-queried foreign keys and filter columns.
    They are created with IF NOT EXISTS so they are safe to run on every startup.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        return

    indexes = [
        ("idx_events_organizer_id", "CREATE INDEX IF NOT EXISTS idx_events_organizer_id ON events(organizer_id)"),
        ("idx_events_venue_id", "CREATE INDEX IF NOT EXISTS idx_events_venue_id ON events(venue_id)"),
        ("idx_events_status", "CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)"),
        ("idx_events_city", "CREATE INDEX IF NOT EXISTS idx_events_city ON events(city)"),
        ("idx_events_start_date", "CREATE INDEX IF NOT EXISTS idx_events_start_date ON events(start_date)"),
        ("idx_events_is_featured", "CREATE INDEX IF NOT EXISTS idx_events_is_featured ON events(is_featured)"),
        ("idx_ticket_tiers_event_id", "CREATE INDEX IF NOT EXISTS idx_ticket_tiers_event_id ON ticket_tiers(event_id)"),
        ("idx_tickets_user_id", "CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)"),
        ("idx_tickets_event_id", "CREATE INDEX IF NOT EXISTS idx_tickets_event_id ON tickets(event_id)"),
        ("idx_tickets_ticket_tier_id", "CREATE INDEX IF NOT EXISTS idx_tickets_ticket_tier_id ON tickets(ticket_tier_id)"),
        ("idx_tickets_verified_by", "CREATE INDEX IF NOT EXISTS idx_tickets_verified_by ON tickets(verified_by_user_id)"),
        ("idx_orders_user_id", "CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)"),
        ("idx_orders_payment_id", "CREATE INDEX IF NOT EXISTS idx_orders_payment_id ON orders(payment_id)"),
        ("idx_order_items_order_id", "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)"),
        ("idx_order_items_tier_id", "CREATE INDEX IF NOT EXISTS idx_order_items_tier_id ON order_items(ticket_tier_id)"),
        ("idx_bookings_venue_id", "CREATE INDEX IF NOT EXISTS idx_bookings_venue_id ON bookings(venue_id)"),
        ("idx_bookings_user_id", "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id)"),
        ("idx_bookings_booking_date", "CREATE INDEX IF NOT EXISTS idx_bookings_booking_date ON bookings(booking_date)"),
        ("idx_reservations_venue_id", "CREATE INDEX IF NOT EXISTS idx_reservations_venue_id ON restaurant_reservations(venue_id)"),
        ("idx_reservations_user_id", "CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON restaurant_reservations(user_id)"),
        ("idx_reservations_event_id", "CREATE INDEX IF NOT EXISTS idx_reservations_event_id ON restaurant_reservations(event_id)"),
        ("idx_notifications_user_id", "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)"),
        ("idx_recaps_event_id", "CREATE INDEX IF NOT EXISTS idx_recaps_event_id ON recaps(event_id)"),
        ("idx_recaps_organizer_id", "CREATE INDEX IF NOT EXISTS idx_recaps_organizer_id ON recaps(organizer_id)"),
        ("idx_recap_likes_recap_id", "CREATE INDEX IF NOT EXISTS idx_recap_likes_recap_id ON recap_likes(recap_id)"),
        ("idx_recap_likes_user_id", "CREATE INDEX IF NOT EXISTS idx_recap_likes_user_id ON recap_likes(user_id)"),
        ("idx_reviews_club_id", "CREATE INDEX IF NOT EXISTS idx_reviews_club_id ON reviews(club_id)"),
        ("idx_reviews_food_spot_id", "CREATE INDEX IF NOT EXISTS idx_reviews_food_spot_id ON reviews(food_spot_id)"),
        ("idx_clubs_city", "CREATE INDEX IF NOT EXISTS idx_clubs_city ON clubs(city)"),
        ("idx_food_spots_city", "CREATE INDEX IF NOT EXISTS idx_food_spots_city ON food_spots(city)"),
        ("idx_food_spots_cuisine", "CREATE INDEX IF NOT EXISTS idx_food_spots_cuisine ON food_spots(cuisine_type)"),
        ("idx_venue_profiles_user_id", "CREATE INDEX IF NOT EXISTS idx_venue_profiles_user_id ON venue_profiles(user_id)"),
        ("idx_organizer_profiles_user_id", "CREATE INDEX IF NOT EXISTS idx_organizer_profiles_user_id ON organizer_profiles(user_id)"),
    ]

    with engine.begin() as conn:
        for name, ddl in indexes:
            try:
                conn.execute(text(ddl))
            except Exception as e:
                print(f"Note while creating index {name}: {e}")


def _seed_platform_defaults() -> None:
    """Seed core Sierra Leone platform defaults for roles, config, and plans."""
    from models_platform import AdminRole, SubscriptionPlan
    from models import SystemConfig, AdminUser, AdminRole as ModelAdminRole
    from auth import get_password_hash

    db = SessionLocal()
    try:
        # Check if seeding is even needed for roles
        existing_roles = db.query(AdminRole).count()
        if existing_roles > 0:
            print(f"Database already seeded with {existing_roles} roles, skipping role seeding")
        else:
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
                    "permissions": ["finance.read", "finance.write"],
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

        # Seed default Admin User only if DEFAULT_ADMIN_PASSWORD is configured
        # This prevents creating an insecure default admin in production
        default_admin_email = settings.DEFAULT_ADMIN_EMAIL
        default_admin_password = settings.DEFAULT_ADMIN_PASSWORD
        if default_admin_password:
            admin_user = db.query(AdminUser).filter(AdminUser.email == default_admin_email).first()
            if not admin_user:
                admin_user = AdminUser(
                    email=default_admin_email,
                    password_hash=get_password_hash(default_admin_password),
                    full_name="Super Admin",
                    role=ModelAdminRole.SUPER_ADMIN,
                    status="active"
                )
                db.add(admin_user)
                print(f"Default admin user created: {default_admin_email}")
        else:
            print("DEFAULT_ADMIN_PASSWORD not set; skipping default admin creation")

        db.commit()
    finally:
        db.close()
