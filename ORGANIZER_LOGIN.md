# Organizer Login Guide

## How Organizer Login Works

Organizers use the **same login endpoint** as all other users. There is no separate organizer login URL.

### Login Endpoint
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "organizer@soundit.test",
  "password": "Test@1234"
}
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 47,
    "email": "organizer@soundit.test",
    "first_name": "DJ",
    "last_name": "FredMax",
    "role": "organizer",
    "status": "active"
  }
}
```

### Frontend Redirect
After successful login, the frontend checks `user.role` and redirects:
- `organizer` → `/dashboard/organizer`
- `venue` → `/dashboard/venue`
- `admin` / `super_admin` → `/admin/dashboard`
- `user` → `/`

---

## Demo/Test Credentials

Run the seed script to create these accounts:
```bash
python scripts/seed_demo_organizers.py
```

| Email | Password | Role | Status | Notes |
|-------|----------|------|--------|-------|
| `organizer@soundit.test` | `Test@1234` | organizer | active | Verified org "Sound It Events" + 2 sample events |
| `organizer2@soundit.test` | `Test@1234` | organizer | active | Unverified org "Weekend Vibes SL" + 1 event |
| `venue@soundit.test` | `Test@1234` | venue | active | "Paddy's Beach Bar" |
| `admin@soundit.test` | `Admin@1234` | admin | active | Platform admin |
| `superadmin@soundit.test` | `Super@1234` | super_admin | active | Super admin |

---

## Key Auth Files

| File | Purpose |
|------|---------|
| `api/auth_password.py` | Register, login, refresh, password reset, profile endpoints |
| `api/auth.py` | JWT creation/validation, password hashing, `get_current_user`, `require_organizer` |
| `models.py` | `User`, `OrganizerProfile`, `UserRole`, `UserStatus` enums |
| `database.py` | DB engine, session, `init_db()` with seeding |
| `app/src/store/authStore.ts` | Frontend Zustand auth store |
| `app/src/pages/auth/Login.tsx` | Frontend login page |

---

## Organizer-Specific API Endpoints

All require `Authorization: Bearer <token>` header and `organizer` role.

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/organizer/dashboard` | Dashboard stats (events, tickets, revenue) |
| `GET /api/v1/organizer/events` | List organizer's events |
| `POST /api/v1/organizer/events` | Create new event (DRAFT) |
| `GET /api/v1/organizer/sales` | Revenue & completed orders |

---

## Registration

Organizers can self-register via:
```
POST /api/v1/auth/register
{
  "email": "new@organizer.com",
  "password": "Strong@1234",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+23278123456",
  "role": "organizer"
}
```

This automatically creates an `OrganizerProfile` with default org name.
