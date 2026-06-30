import sys
sys.path.insert(0, '.')

from database import SessionLocal
from models import User, UserRole, UserStatus, City
from auth import get_password_hash
from datetime import datetime

db = SessionLocal()

# Check if user already exists
existing = db.query(User).filter(User.email == "organizer@sounditentsl.com").first()
if existing:
    print("User already exists")
    db.close()
    sys.exit(0)

user = User(
    email="organizer@sounditentsl.com",
    password_hash=get_password_hash("0ganizer!23"),
    first_name="Test",
    last_name="Organizer",
    role=UserRole.ORGANIZER,
    status=UserStatus.ACTIVE,
    is_verified=True,
    phone="",
    preferred_city=City.FREETOWN,
    created_at=datetime.utcnow(),
)
db.add(user)
db.commit()
print(f"Organizer created with ID: {user.id}")
db.close()
