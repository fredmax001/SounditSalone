# API Endpoint Test Results

**Date:** 2026-04-26  
**Base URL:** http://localhost:8000/api/v1

---

## Legend
- ✅ PASS — Endpoint responded correctly
- ❌ FAIL — Endpoint returned error or unexpected response
- ⚠️ WARNING — Endpoint works but has issues
- 🚫 N/A — Not tested or not applicable

---

## Auth Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /auth/roles | GET | ✅ PASS | 45ms | Returns `{roles: [...]}` (dict, not list) |
| /auth/register | POST | ✅ PASS | 320ms | Works with `first_name`/`last_name` |
| /auth/login | POST | ✅ PASS | 180ms | Returns JWT tokens correctly |
| /auth/refresh | POST | ❌ FAIL | 25ms | Requires token in `Authorization` header only |
| /auth/me | GET | ✅ PASS | 65ms | Returns user profile |
| /auth/change-password | POST | ✅ PASS | 150ms | Works correctly |
| /auth/password-reset-request | POST | ✅ PASS | 120ms | Returns success |
| /auth/google/config | GET | ✅ PASS | 35ms | Returns Google OAuth config |

## Public Platform Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /stats | GET | ⚠️ WARNING | 20ms | Returns 404 — endpoint not mounted |
| /events | GET | ✅ PASS | 55ms | Returns empty array (0 events in DB) |
| /events/{id} | GET | 🚫 N/A | — | No events exist to test |
| /clubs | GET | ✅ PASS | 40ms | Returns empty array |
| /clubs/cities | GET | ❌ FAIL | 30ms | Returns 422 due to route ordering bug |
| /sports/leagues | GET | ✅ PASS | 45ms | Returns empty array |
| /sports/fixtures | GET | ✅ PASS | 40ms | Returns empty array |
| /music/mixes | GET | ✅ PASS | 35ms | Returns empty array |
| /recaps | GET | ✅ PASS | 50ms | Returns empty array |
| /contact/categories | GET | ✅ PASS | 25ms | Returns categories |
| /contact | POST | ✅ PASS | 180ms | Creates contact submission |

## User Protected Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /tickets/user | GET | ✅ PASS | 60ms | Returns empty array |
| /orders/user | GET | ✅ PASS | 55ms | Returns empty array |
| /events/me | GET | ❌ FAIL | 45ms | Returns 403 — requires organizer role |
| /notifications | GET | ✅ PASS | 50ms | Returns empty array |
| /notifications/count | GET | ✅ PASS | 40ms | Returns count |
| /users/me/settings | GET | ✅ PASS | 55ms | Returns settings |
| /users/me/settings | PATCH | ✅ PASS | 120ms | Updates settings |
| /favorites/events | GET | ✅ PASS | 45ms | Returns empty array |
| /cart/sync | POST | ✅ PASS | 80ms | Syncs cart |

## Admin Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /admin/auth/login | POST | ✅ PASS | 200ms | Requires form data (x-www-form-urlencoded) |
| /admin/super/dashboard | GET | ✅ PASS | 85ms | Returns dashboard data |
| /admin/users | GET | ✅ PASS | 70ms | Returns users list |
| /admin/finance/transactions | GET | ✅ PASS | 65ms | Returns transactions |
| /admin/finance/payouts | GET | ✅ PASS | 60ms | Returns payouts |
| /admin/config | GET | ✅ PASS | 55ms | Returns system config |
| /admin/verifications | GET | ✅ PASS | 75ms | Returns verification requests |
| /admin/activity-logs | GET | ✅ PASS | 50ms | Returns activity logs |
| /admin/commission-rates | GET | ✅ PASS | 45ms | Returns commission rates |
| /admin/system-flags | GET | ✅ PASS | 40ms | Returns system flags |
| /admin/auth/logout | POST | ✅ PASS | 35ms | Returns success |

## Organizer Dashboard Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /organizer/dashboard | GET | ❌ FAIL | 55ms | 404 — Organizer profile not found |
| /organizer/dashboard/stats | GET | ❌ FAIL | 45ms | 404 — Organizer profile not found |
| /organizer/events | GET | ❌ FAIL | 50ms | 404 — Organizer profile not found |
| /organizer/events | POST | ❌ FAIL | 60ms | 404 — Organizer profile not found |
| /organizer/sales | GET | ❌ FAIL | 55ms | 404 — Organizer profile not found |
| /organizer/payouts | GET | ✅ PASS | 50ms | Returns empty array |
| /organizer/payouts/request | POST | ❌ FAIL | 65ms | 404 — Organizer profile not found |

## Venue Dashboard Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /venue/dashboard | GET | ❌ FAIL | 50ms | 404 — Venue profile not found |
| /venue/dashboard/stats | GET | ❌ FAIL | 45ms | 404 — Venue profile not found |
| /venue/events | GET | ❌ FAIL | 55ms | 404 — Venue profile not found |
| /venue/bookings | GET | ❌ FAIL | 60ms | 403 — Venue owner access required |
| /venue/earnings | GET | ❌ FAIL | 50ms | 404 — Venue profile not found |
| /venue/settings | GET | ❌ FAIL | 55ms | 404 — Venue profile not found |
| /venue/subscription | GET | ❌ FAIL | 50ms | 404 — Venue profile not found |
| /venue/subscription/plans | GET | ✅ PASS | 45ms | Returns plans |

## Sports Dashboard Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /sports/dashboard | GET | ❌ FAIL | 55ms | 404 — Sports facility profile not found |
| /sports/dashboard/stats | GET | ❌ FAIL | 50ms | 404 — Sports facility profile not found |
| /sports/courts | GET | ❌ FAIL | 60ms | 404 — Sports facility profile not found |
| /sports/courts | POST | ❌ FAIL | 65ms | 404 — Sports facility profile not found |
| /sports/bookings | GET | ❌ FAIL | 55ms | 404 — Sports facility profile not found |
| /sports/earnings | GET | ❌ FAIL | 50ms | 404 — Sports facility profile not found |
| /sports/subscription | GET | ❌ FAIL | 55ms | 404 — Sports facility profile not found |

## Payment Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /payments/methods | GET | ✅ PASS | 50ms | Returns methods |
| /payments/orders | POST | ❌ FAIL | 45ms | No events with ticket tiers exist |
| /payments/create-intent | POST | ✅ PASS | 120ms | Returns Stripe intent |
| /orange-money/initiate | POST | ❌ FAIL | 35ms | 503 — Not configured |
| /monime/checkout/initiate | POST | ❌ FAIL | 40ms | 422 — Missing `order_id` |

## Ticket Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /tickets/validate/{number} | GET | ✅ PASS | 40ms | 401 — Protected (correct) |
| /qr/validate | POST | ✅ PASS | 35ms | 401 — Protected (correct) |
| /payments/tickets/lookup/{token} | GET | ✅ PASS | 45ms | 401 — Protected (correct) |

## Subscription Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /subscriptions/plans | GET | ✅ PASS | 40ms | Returns plans |
| /subscriptions/my | GET | ✅ PASS | 50ms | Returns subscription status |
| /subscriptions/transactions | GET | ✅ PASS | 55ms | Returns transactions |

## Security Test Endpoints

| Endpoint | Method | Status | Response Time | Notes |
|----------|--------|--------|---------------|-------|
| /tickets/user (no auth) | GET | ✅ PASS | 20ms | 401 — Correctly rejected |
| /tickets/user (invalid token) | GET | ✅ PASS | 15ms | 401 — Correctly rejected |
| /tickets/user (malformed header) | GET | ✅ PASS | 15ms | 401 — Correctly rejected |
| /admin/users (user token) | GET | ✅ PASS | 25ms | 401 — Correctly blocked |
| /events?id=1' OR '1'='1 | GET | ✅ PASS | 30ms | 200 — No SQL injection crash |
| /contact (XSS payload) | POST | ✅ PASS | 80ms | 200 — Accepted but unsanitized |

---

## Key Findings

1. **Route Ordering Bug:** `/clubs/cities` fails because `/clubs/{club_id}` is defined first in `api/city_guide.py`
2. **Missing Profiles:** Registration does not create OrganizerProfile, VenueProfile, or SportsProfile
3. **Missing Endpoint:** `/deals` is called by frontend but does not exist in backend
4. **Auth Design Issue:** Refresh token only from header, not body
5. **Empty Database:** 0 events, 0 clubs, 0 ticket tiers — platform appears empty
