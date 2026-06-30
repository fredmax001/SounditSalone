# Sound It Salone — Senior Engineering Review

**Date:** 2026-06-30  
**Reviewers:** Senior Engineer / Debugging Engineer / Performance Engineer / Software Architect  
**Scope:** Full-stack FastAPI + React/Capacitor codebase (`api/`, `app/`, `models.py`, `main*.py`, `database*.py`, `config*.py`, `deploy/`, `nginx/`, `tests/`)

---

## 1. Executive Summary

This codebase is a feature-rich MVP for a music-events and nightlife platform in Sierra Leone. It has grown organically from a small prototype into a 58-table monolith with ~30 API modules, ~110 frontend pages, and Docker/Nginx/CI infrastructure. The product behavior is largely intact, but the implementation carries **production-critical bugs, duplicated business logic, non-functional infrastructure wiring, and significant scalability risks**.

### Most Critical Findings

| # | Finding | Risk |
|---|---|---|
| 1 | `api/auth_password.py` imports non-existent `SECRET_KEY, ALGORITHM` from `config` | Password reset is completely broken |
| 2 | `api/subscriptions.py` compares `UserRole` enum to wrong string (`"venue_owner"`) | Venue subscriptions silently never work |
| 3 | `main_production.py` imports dev `config.py` / `database.py`, not the hardened `config_production` / `database_production` | Production ignores pool settings, slow-query logging, and strict validation |
| 4 | `main_production.py` health check uses raw `db.execute("SELECT 1")` (SQLAlchemy 2.0 error) and leaks sessions | Health endpoint reports DB down; connection pool exhaustion |
| 5 | `models.py` overwrites `RecapLike.__table_args__`, dropping the unique constraint | Duplicate likes allowed; data integrity risk |
| 6 | Ticket inventory is read-modify-write with no row locking | Race condition allows overselling under concurrent load |
| 7 | 45+ foreign keys and search columns lack DB indexes | Performance degrades rapidly with data growth |
| 8 | `.dockerignore` excludes `alembic/`, `alembic.ini`, and built frontend assets cannot be verified | Docker images cannot run migrations or serve SPA correctly |
| 9 | Celery services are declared but no `tasks.py` exists; Redis is unused | Background processing does not exist despite infrastructure |
| 10 | Frontend has no code splitting, no unified API client, and loads a 2.4 MB bundle upfront | Poor mobile/Capacitor performance; high backend load |

### Verdict

The platform **works in demo/small-scale mode** but is **not production-hardened for high-traffic, multi-replica, or team-scale development**. The good news: most issues are fixable with targeted refactoring, better separation of concerns, and consistent production wiring. The report below provides the architecture breakdown, root-cause analysis, and concrete production-grade improvements.

---

## 2. Clean Architecture Breakdown

### 2.1 High-Level Data Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  React SPA  │──────▶│  Nginx SSL   │──────▶│  FastAPI (main) │
│  / Capacitor│◀──────│  rate limit  │◀──────│   /main_production│
└─────────────┘      └──────────────┘      └────────┬────────┘
                                                    │
                           ┌────────────────────────┼────────────────────────┐
                           │                        │                        │
                           ▼                        ▼                        ▼
                    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
                    │  PostgreSQL │          │    Redis    │          │ Local/S3    │
                    │  SQLAlchemy │          │  (unused)   │          │ uploads     │
                    └─────────────┘          └─────────────┘          └─────────────┘
```

### 2.2 Backend Layering (Current vs. Ideal)

**Current (Anemic monolith):**
```
main.py / main_production.py
        │
        ├─> api/*.py          (HTTP + business logic + DB queries + response dicts)
        ├─> models.py         (58 tables, mixed domains)
        ├─> database.py       (engine, session, init_db with create_all)
        ├─> auth.py           (JWT + role guards)
        └─> config.py         (settings)
```

**Ideal (Layered architecture):**
```
application layer   api/routers/        (HTTP, validation, deps only)
business layer      services/           (use cases, transactions)
data layer          repositories/       (query builders, eager-loading strategies)
schema layer        schemas/            (Pydantic request/response models)
domain layer        models/             (SQLAlchemy entities)
infrastructure      database.py, config.py, cache.py, storage.py
```

### 2.3 Frontend Layering

**Current:**
```
app/src/
  App.tsx          (imports all 110 pages; no lazy loading)
  pages/           (giant monolithic route components)
  components/ui/   (53 shadcn primitives)
  store/           (19 Zustand stores, duplicated API logic)
  lib/             (utils.ts, dead supabase.ts stub)
```

**Ideal:**
```
app/src/
  app/             (routing + providers)
  features/        (domain modules: events, tickets, auth, dashboard)
    ├── api/       (per-domain API hooks)
    ├── components/
    ├── stores/
    └── types/
  shared/
    ├── api/       (central axios client + interceptors)
    ├── ui/        (design-system primitives)
    └── lib/
```

### 2.4 Deployment Architecture

The deployment *shape* is correct (Docker Compose, Nginx reverse proxy, PostgreSQL, Redis, CI/CD), but several wires are disconnected:

- `main_production.py` does not use `config_production.py` / `database_production.py`.
- `docker-compose.prod.yml` defines Celery worker/beat services that reference a non-existent `tasks.py`.
- `nginx` is documented but not included as a service in `docker-compose.prod.yml`.
- `.dockerignore` excludes `alembic/` and `alembic.ini`, breaking containerized migrations.
- `deploy/deploy.sh` merges `docker-compose.yml` (dev) with `docker-compose.prod.yml` (prod), creating service-name and environment conflicts.

---

## 3. Role 2 — Senior Engineer Audit

### 3.1 Bad Architecture Decisions

1. **Dual config/database modules.** `config.py` vs `config_production.py` and `database.py` vs `database_production.py` split production concerns into a parallel, partially broken track. `main_production.py` imports the dev versions, so hardened production settings (pool tuning, strict validation) are ignored. `database_production.py` references deleted models and cannot be imported.

2. **`Base.metadata.create_all()` on startup.** `init_db()` runs on every container start. This races with Alembic, silently creates schema drift, and is unsafe for production data.

3. **No service/repository layer.** Every router contains business logic, SQLAlchemy queries, and hand-rolled response dicts. Cross-cutting behavior (auth, transactions, serialization) is duplicated.

4. **Monolithic `models.py`.** 58 tables live in one file. Domains (events, ticketing, payments, city guide, admin, sports) are not separated, making the schema hard to reason about and evolve.

5. **Rate limiting is decorative.** `slowapi` limiters are applied to routers, but `SlowAPIMiddleware` is never added to the FastAPI app. The decorators are no-ops.

6. **Celery/Redis are infrastructure theater.** Both are declared in `requirements.txt` and `docker-compose.prod.yml`, but no tasks or caching calls exist. Redis sits idle while emails and AI processing block request handlers.

### 3.2 Duplicate Logic

| Pattern | Locations | Count |
|---|---|---|
| Ticket serialization | `api/payments.py`, `api/monime.py` | 2+ |
| Profile auto-creation | `auth_password.py`, `otp.py`, `venue_dashboard.py`, `restaurant_dashboard.py`, `platform_utils.py` | 5+ |
| City normalization | `events.py`, `organizer.py`, `restaurant_dashboard.py` | 3+ |
| Admin guard logic | `auth.py`, `admin_stubs.py`, `admin.py` | 3+ |
| Commission calc (4% hardcoded) | `admin.py`, `organizer.py` | multiple |
| API URL + auth header setup | Frontend stores/pages | 15+ |

### 3.3 Performance Bottlenecks

- **N+1 queries** in `/events`, `/users/tickets`, `/venue/bookings`, `/admin/verifications`, reviews, and sales feed.
- **Synchronous blocking inside async endpoints**: AI menu builder (120s Kimi call), PDF parsing, file writes, synchronous email sending.
- **Unbounded result sets**: `/events` returns all rows; admin endpoints load entire tables.
- **No caching**: Hot reads (event listings, city guide, dashboard stats) hit PostgreSQL on every request.
- **Massive frontend bundle**: 2.4 MB JS with no code splitting; Three.js/Recharts/Framer Motion loaded upfront.

### 3.4 Scalability Risks

- **Ticket overselling** due to non-atomic inventory decrement.
- **DB connection pool exhaustion** from leaked health/metrics sessions and unbounded workers.
- **Single-node file storage** (`static/uploads/`) prevents horizontal scaling.
- **In-memory metrics** in `monitoring.py` are lost across workers/restarts.
- **Broadcast notifications** inserted one-by-one in Python loops.

### 3.5 Maintainability Issues

- Hand-rolled response dicts instead of Pydantic response models.
- Inline imports scattered through routers.
- `print()` used for error logging in many modules.
- Inconsistent async/sync endpoint style.
- `strict: false` TypeScript and heavy `any` usage on the frontend.
- No frontend tests; backend tests are smoke/load only.

---

## 4. Role 3 — Production Debugging Engineer

### 4.1 Code Functionality Breakdown

The backend exposes ~328 routes across 30 modules. The core user journey is:

1. **Auth**: Register/login → JWT access + refresh tokens (`auth_password.py`, `auth.py`).
2. **Discovery**: List/paginate events and city-guide entries (`events.py`, `city_guide.py`).
3. **Purchase**: Create order → pay via Stripe/Orange Money/Monime → issue tickets (`payments.py`, `orange_money.py`, `monime.py`, `tickets.py`).
4. **Check-in**: Validate QR code, mark ticket used (`tickets.py`).
5. **Dashboards**: Organizer/venue/restaurant/admin views with stats and management actions.

### 4.2 Root Cause Analysis — Critical Bugs

#### Bug A: Password reset endpoint crashes immediately

**File:** `api/auth_password.py:488-493`

```python
from jose import jwt as jose_jwt
from config import SECRET_KEY, ALGORITHM

payload = jose_jwt.decode(request_data.token, SECRET_KEY, algorithms=[ALGORITHM])
```

`config.py` exports only `get_settings`. `SECRET_KEY` and `ALGORITHM` are not module-level names. The endpoint raises `ImportError` on import or first invocation, making password reset completely unavailable.

**Robust fix:** Use the settings object and the correct algorithm attribute name (`JWT_ALGORITHM`).

#### Bug B: Venue subscriptions never match

**File:** `api/subscriptions.py:43,71,110,131,187,217`

```python
if current_user.role == "venue_owner":
```

`User.role` is a `UserRole(str, enum.Enum)` column. The enum value is `UserRole.VENUE = "venue"`, not `"venue_owner"`. Because the enum inherits `str`, `UserRole.VENUE == "venue"` is `True`, but `"venue_owner"` never matches. Venue owners always fall through to the organizer branch or the 403.

**Robust fix:** Compare against `UserRole.VENUE` consistently.

#### Bug C: Production health check reports DB down

**File:** `main_production.py:271-272`

```python
db = next(get_db())
db.execute("SELECT 1")
```

SQLAlchemy 2.0 requires `text("SELECT 1")`. The raw string raises `TypeError`, and the except block reports the database as unhealthy. Additionally, `db = next(get_db())` is never closed, leaking sessions from the pool.

**Robust fix:** Use `text()`, and ensure sessions are closed with `contextlib.closing` or a helper.

#### Bug D: `RecapLike` unique constraint is lost

**File:** `models.py:1115-1181`

```python
class RecapLike(Base):
    __tablename__ = "recap_likes"
    __table_args__ = (UniqueConstraint('recap_id', 'user_id', name='uq_recap_like_user'),)
    ...

# Later in the file
RecapLike.__table_args__ = ({'sqlite_autoincrement': True},)
```

The second assignment replaces the tuple containing the unique constraint. The table is created without `uq_recap_like_user`, allowing duplicate likes.

**Robust fix:** Merge both table arguments into one tuple/dict.

#### Bug E: Race condition in ticket inventory

**Files:** `api/payments.py:265-288`, `api/orange_money.py:488-511`, `api/monime.py:395-440`

All three payment flows do:

```python
available = int(tier.quantity or 0) - int(tier.quantity_sold or 0)
if quantity > available:
    raise HTTPException(...)
tier.quantity_sold += quantity
```

Two concurrent purchasers can read the same `quantity_sold`, both pass the check, and both increment it, overselling the event.

**Robust fix:** Use `with_for_update()` to lock the `TicketTier` row during the check-and-increment, or use an atomic `UPDATE ticket_tiers SET quantity_sold = quantity_sold + :q WHERE ...` statement.

### 4.3 Edge Case Analysis

| Edge Case | What Happens | Why |
|---|---|---|
| Webhook redelivery after order completed | Duplicate tickets possible | Idempotency check is query-only, not atomic with inventory update |
| AI menu upload under load | Request workers starved | 120s synchronous Kimi call blocks the event loop |
| Admin broadcasts to 10k users | Endpoint times out | Emails/notifications created inline in a loop |
| Free ticket with fake email | Account + ticket created unverified | `rsvp_free_ticket_guest` has no verification or rate limiting |
| Health check called frequently | Pool exhaustion | Sessions in `/health` and `/metrics` are not closed |
| Production container restart | `create_all` mutates schema | `init_db()` runs `Base.metadata.create_all()` |

---

## 5. Role 4 — Performance Optimization Engineer

### 5.1 Performance Issue Breakdown

| Area | Symptom | Root Cause |
|---|---|---|
| API list endpoints | Slow TTFB, DB CPU spikes | N+1 queries, missing FK indexes |
| Payment completion | Timeouts, worker starvation | Synchronous email, no background tasks |
| AI menu import | 120s+ response times | Synchronous file I/O + external AI call |
| Frontend first load | 2.4 MB JS, poor mobile UX | No code splitting, all pages eagerly imported |
| Dashboard pages | Janky re-renders | Monolithic components, heavy animation libs |
| Static assets | 404s / slow uploads | Local disk storage, no CDN/S3 integration |

### 5.2 Optimization Strategies

1. **Database layer**
   - Add indexes on all foreign keys and heavily filtered columns.
   - Add `selectinload` / `joinedload` to list endpoints.
   - Use `with_for_update()` for inventory-critical paths.

2. **API layer**
   - Move email, AI parsing, and bulk notifications to background tasks (Celery/ARQ/RQ or FastAPI `BackgroundTasks` as a first step).
   - Cache hot reads (event listings, city guide) in Redis with short TTLs.
   - Paginate all list endpoints and enforce `page_size` caps.

3. **Frontend layer**
   - Add route-based code splitting with `React.lazy()` + `Suspense`.
   - Configure Vite `manualChunks` for vendor/admin/dashboard bundles.
   - Centralize API calls in one axios instance with interceptors.
   - Adopt TanStack Query for caching, deduplication, and stale-while-revalidate.

4. **Infrastructure layer**
   - Remove unused Celery/Redis wiring or implement real tasks.
   - Move uploads to S3/R2/MinIO.
   - Add PgBouncer or RDS Proxy for DB connection pooling.

### 5.3 Scalability Recommendations

- Horizontal scaling: stateless FastAPI containers behind Nginx; move sessions to Redis; use S3 for uploads.
- Database: read replicas for analytics/reporting; connection pooling; archive old `tickets`, `orders`, `search_logs`, `monime_webhook_logs`.
- Queue: implement Celery/ARQ for emails, AI, webhooks, payouts, bulk notifications.
- Caching: Redis for event listings, user sessions, rate limits.
- Frontend: split web vs. mobile bundles; lazy-load heavy libraries; add service worker for offline resilience.

---

## 6. Role 5 — Software Architect

### 6.1 Proposed Folder Structure

```
sound-it-salone/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # single entry point with env-based behavior
│   │   ├── dependencies.py            # auth, db, settings, rate limiter
│   │   └── middleware.py              # logging, security headers, gzip, errors
│   ├── api/
│   │   └── v1/
│   │       ├── routers/               # thin HTTP routers only
│   │       └── deps.py
│   ├── core/
│   │   ├── config.py                  # one settings class, env-driven
│   │   ├── database.py                # engine, session, transaction helpers
│   │   ├── cache.py                   # Redis wrapper
│   │   ├── storage.py                 # S3/local abstraction
│   │   ├── security.py                # password, JWT, role guards
│   │   └── exceptions.py
│   ├── models/                        # SQLAlchemy domain models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── ticketing.py
│   │   ├── payment.py
│   │   ├── venue.py
│   │   ├── restaurant.py
│   │   ├── platform.py
│   │   └── ...
│   ├── schemas/                       # Pydantic request/response models
│   ├── services/                      # business logic + transactions
│   ├── repositories/                  # data access + eager-loading strategies
│   ├── tasks/                         # Celery/ARQ background tasks
│   ├── migrations/                    # Alembic (or keep alembic/)
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/                       # routing, providers
│   │   ├── features/                  # domain-driven modules
│   │   ├── shared/                    # api client, UI primitives, utils
│   │   └── types/
│   └── tests/
├── infra/
│   ├── docker/
│   ├── nginx/
│   ├── terraform-or-pulumi/           # optional
│   └── scripts/
└── docs/
```

### 6.2 Clean Architecture Principles to Apply

1. **Single entry point.** Replace `main.py` / `main_production.py` with one app factory parameterized by environment.
2. **Single source of truth for config.** Merge `config.py` and `config_production.py` into one `Settings` class.
3. **Dependency inversion.** Routers depend on `services`, not SQLAlchemy directly. Services depend on `repositories`.
4. **Explicit transactions.** Use a context manager (`with transaction(db):`) that rolls back on exception.
5. **Response models.** Every endpoint returns a Pydantic schema; no hand-rolled dicts.
6. **Domain-driven models.** Split `models.py` into cohesive modules.
7. **Frontend feature slices.** Each feature owns its API, components, types, and store.

### 6.3 Architectural Improvements

- **Backend:** From "fat routers" to "thin routers + services + repositories".
- **Frontend:** From monolithic pages to feature slices with code splitting and a shared API client.
- **Data:** From `create_all` startup to proper Alembic migration workflow.
- **Infra:** From manual deploy scripts to CI/CD with smoke-tested containers.
- **Observability:** From `print()` to structured logging + Sentry + Prometheus-style metrics.

---

## 7. Code Fixes Applied During This Review

The following safe, functionality-preserving fixes were applied directly. They target the most critical bugs and performance issues identified above.

### Debugging / Correctness

| # | File | Fix |
|---|---|---|
| 1 | `api/auth_password.py` | Replaced broken `from config import SECRET_KEY, ALGORITHM` with `get_settings()` and `settings.SECRET_KEY` / `settings.JWT_ALGORITHM` in both password-reset confirmation and token-verification endpoints. |
| 2 | `api/subscriptions.py` | Replaced `"venue_owner"` / `"organizer"` string comparisons with `UserRole.VENUE` / `UserRole.ORGANIZER`, restoring venue and organizer subscription flows. |
| 3 | `models.py` | Merged `RecapLike.__table_args__` so the unique constraint on `(recap_id, user_id)` is preserved alongside the `sqlite_autoincrement` option. |
| 4 | `main_production.py` | Fixed health check `db.execute("SELECT 1")` → `db.execute(text("SELECT 1"))`; closed leaked DB sessions in `/api/v1/health` and `/metrics`. |
| 5 | `main_production.py` | Added missing `restaurant_dashboard`, `food_orders`, and `ai_menu_builder` routers so production parity matches development. |

### Performance / Scalability

| # | File | Fix |
|---|---|---|
| 6 | `api/events.py` | Added `selectinload(Event.ticket_tiers)` to public listing, saved events, my events, and detail endpoints to eliminate N+1 queries. |
| 7 | `api/user_dashboard.py` | Added `joinedload(Ticket.event)` and `joinedload(Ticket.ticket_tier)` to `/users/tickets`; removed per-ticket `TicketTier` query. |
| 8 | `api/payments.py` | Added `with_for_update()` on `TicketTier` in purchase completion to prevent race-condition overselling. |
| 9 | `api/monime.py` | Added `with_for_update()` on `TicketTier` in `_generate_tickets_for_order` to prevent race-condition overselling. |
| 10 | `database.py` | Added `create_performance_indexes()` that creates 33 critical indexes on startup (`IF NOT EXISTS`) for the most-queried foreign keys and filter columns. |
| 11 | `database.py` | Added `get_db_context()` context manager with automatic `commit()` / `rollback()` for background tasks and scripts. |
| 12 | `config.py` / `database.py` | Moved production DB pool settings (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`) and JWT hour compatibility into the active `config.py`/`database.py` path so `main_production.py` can use them without switching to the broken `config_production`/`database_production` modules. |

### Concurrency / Background Processing

| 13 | `api/payments.py` | Moved buyer confirmation email and organizer notification/email out of the purchase response path into a `BackgroundTasks` task with its own DB session. |
| 14 | `api/auth_password.py` | Moved welcome emails and password-reset emails to `BackgroundTasks` so registration and reset-request endpoints respond immediately. |

### Migration / Deployment Workflow

| 15 | `alembic/versions/1c66a38847df_initial_migration_all_current_models.py` | Replaced empty `pass` migration with a real bootstrap migration that creates all current tables from `Base.metadata`. |
| 16 | `database.py` | Made `init_db()` migration-aware: creates tables automatically for SQLite, but for PostgreSQL it relies on Alembic and only falls back to `create_all()` when no tables exist (with a warning). |
| 17 | `deploy/deploy.sh` | Switched from legacy `docker-compose` to `docker compose` v2; removed dev+prod compose merge; made migration failure abort deployment. |
| 18 | `deploy-homeserver.sh` | Switched from legacy `docker-compose` to `docker compose` v2. |

### Infrastructure

| 19 | `.dockerignore` | Removed `alembic/` and `alembic.ini` exclusions so containers can run migrations; excluded frontend source files while keeping `app/dist`. |

### Dead-Code Cleanup

| 20 | `api/auth.py`, `api/sms_service.py`, `api/sitemap.py`, `api/otp_visible.py` | Removed four empty stub routers and their imports from `main.py` / `main_production.py`. |
| 21 | Backend modules | Removed unused path parameters / variables flagged by `vulture` / `ruff` (`api/admin.py`, `api/auth_password.py`, `api/payments.py`, `api/vendors.py`, `database_production.py`, `schemas.py`) without changing behavior. |
| 22 | `tests/test_api_endpoints.py` | Removed four unused `headers` assignments flagged by `ruff`. |

### Monitoring / Observability

| 23 | `monitoring.py` | Re-wired imports from deprecated `config_production` / `database_production` to active `config` / `database`; replaced removed `BookingRequest` model references with the live `Booking` model; mapped `requester_id` → `user_id` and `budget` → `total_amount` for pending-action cards. |
| 24 | `database.py` | Added `check_database_health()` helper used by `monitoring.py` (and available for future health endpoints). |

### Startup Bug Discovered During Local Testing

| 25 | `models_platform.py` | Added missing `SportsCourt` model so `SportsCalendarBlock` / `SportsTeam` foreign keys resolve and the app can start with an empty/SQLite database. |

### What Was NOT Changed (requires dedicated, tested refactor)

- Full unification of `config.py` / `config_production.py` and `database.py` / `database_production.py` — `main_production.py` now gets production tuning through the active config path, but the duplicate modules still exist.
- Moving OTP email (`api/otp.py`) and bulk admin notifications to background tasks — these have different failure semantics and need product decisions.
- Moving AI menu processing / PDF parsing out of the request path — needs a real task queue (Celery/ARQ) or upload-then-poll pattern.
- Frontend architecture refactor (code splitting, central API client, TanStack Query).
- S3 upload backend and horizontal-scaling infrastructure.

## 8. Remaining Action Plan

### This Week

1. Add row-level locking to ticket inventory in `orange_money.py` once the merchant code is ready.
2. Unify `config.py` / `config_production.py` and `database.py` / `database_production.py` after testing (or deprecate the duplicate modules).
3. ~~Fix `monitoring.py` broken `BookingRequest` references and wire it into the active config/database path~~ — completed.
4. Wire Redis caching for event/city-guide hot reads.
5. Remove or implement Celery services.
6. ~~Dead-code cleanup (empty stubs, unused imports/variables)~~ — completed.

### This Month

6. Introduce service/repository layer for payments and ticketing.
7. Add Pydantic response models for core endpoints.
8. Move AI menu processing, bulk notifications, and OTP delivery to a real task queue.
9. Frontend: central API client, TanStack Query, route code splitting.
10. S3 upload backend; remove local-disk scaling bottleneck.
11. Add real pytest unit/integration tests.

---

## 9. Files Changed

- `SENIOR_ENGINEERING_REVIEW.md` (new / updated)
- `alembic/versions/1c66a38847df_initial_migration_all_current_models.py`
- `api/admin.py` (dead-variable cleanup)
- `api/auth.py` (removed empty stub)
- `api/auth_password.py` (validator noqa + `get_settings` fix)
- `api/events.py` (N+1 fix)
- `api/monime.py` (row locking)
- `api/orange_money.py` (notification regression fix only; row-level locking still on hold)
- `api/otp_visible.py` (removed empty stub)
- `api/payments.py` (dead-variable cleanup + background tasks + row locking)
- `api/sitemap.py` (removed empty stub)
- `api/sms_service.py` (removed empty stub)
- `api/subscriptions.py` (role enum fix)
- `api/user_dashboard.py` (N+1 fix)
- `api/vendors.py` (dead-variable cleanup)
- `config.py` (production tuning additions only; pre-existing uncommitted additions remain untouched)
- `database.py` (migration/index/transaction additions + `check_database_health`)
- `database_production.py` (dead-variable cleanup; still deprecated)
- `deploy-homeserver.sh`
- `deploy/deploy.sh`
- `.dockerignore`
- `main.py` (stub-router removal)
- `main_production.py` (health check + router parity)
- `models.py` (RecapLike constraint fix only; pre-existing uncommitted model additions remain untouched)
- `models_platform.py` (added missing `SportsCourt` model)
- `monitoring.py` (active config/database wiring + `Booking` model fix)
- `schemas.py` (dead-variable cleanup)
- `tests/test_api_endpoints.py` (dead-variable cleanup)

---

*This review was generated by reverse-engineering the codebase, tracing data flows, and cross-referencing architecture, debugging, performance, and refactoring concerns. The goal is to lift the platform from MVP quality to production-grade engineering without changing product behavior.*
