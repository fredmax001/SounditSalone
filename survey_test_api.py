#!/usr/bin/env python3
"""
Sound It Salone - Comprehensive API Production Survey
Tests every API endpoint and records results.
"""

import requests
import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"
RESULTS: List[Dict] = []

@dataclass
class TestContext:
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[int] = None
    event_id: Optional[int] = None
    venue_id: Optional[int] = None
    ticket_id: Optional[int] = None
    order_id: Optional[int] = None
    admin_token: Optional[str] = None
    organizer_token: Optional[str] = None
    venue_token: Optional[str] = None
    sports_token: Optional[str] = None
    ticket_tier_id: Optional[int] = None

def record(module: str, feature: str, test_case: str, status: str, notes: str = "", priority: str = "Medium", response_time_ms: float = 0.0, endpoint: str = "", method: str = "", status_code: int = 0):
    RESULTS.append({
        "module": module,
        "feature": feature,
        "test_case": test_case,
        "status": status,
        "notes": notes,
        "priority": priority,
        "response_time_ms": round(response_time_ms, 2),
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat()
    })
    icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️", "N/A": "🚫"}.get(status, "?")
    print(f"{icon} [{module}] {feature} — {test_case} ({status}) {notes}")

def req(method: str, endpoint: str, **kwargs) -> tuple:
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    try:
        resp = requests.request(method, url, timeout=15, **kwargs)
        elapsed = (time.time() - start) * 1000
        return resp, elapsed
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        class FakeResp:
            status_code = 0
            text = str(e)
            def json(self): return {"detail": str(e)}
        return FakeResp(), elapsed

# ============================================================
# MODULE 1: AUTHENTICATION
# ============================================================
def test_auth(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 1: AUTHENTICATION")
    print("="*60)

    # 1.1 Get roles
    resp, elapsed = req("GET", "/auth/roles")
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            record("Auth", "Roles", "Get available roles", "PASS", f"Found {len(data)} roles", "Critical", elapsed, "/auth/roles", "GET", resp.status_code)
        else:
            record("Auth", "Roles", "Get available roles", "FAIL", "Empty roles list", "Critical", elapsed, "/auth/roles", "GET", resp.status_code)
    else:
        record("Auth", "Roles", "Get available roles", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/auth/roles", "GET", resp.status_code)

    # 1.2 Register a test user
    unique = str(uuid.uuid4())[:8]
    test_email = f"testuser_{unique}@example.com"
    test_phone = f"+23277{unique}"
    test_password = "TestPass123!"

    resp, elapsed = req("POST", "/auth/register", json={
        "email": test_email,
        "phone": test_phone,
        "password": test_password,
        "first_name": "Test",
        "last_name": f"User{unique}",
        "role": "user"
    })
    if resp.status_code == 200 or resp.status_code == 201:
        data = resp.json()
        ctx.access_token = data.get("access_token")
        ctx.refresh_token = data.get("refresh_token")
        ctx.user_id = data.get("user", {}).get("id")
        record("Auth", "Register", "Register with valid data", "PASS", f"User ID: {ctx.user_id}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
    else:
        record("Auth", "Register", "Register with valid data", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)

    # 1.3 Register duplicate
    if ctx.access_token:
        resp, elapsed = req("POST", "/auth/register", json={
            "email": test_email,
            "phone": test_phone,
            "password": test_password,
            "first_name": "Duplicate",
            "last_name": "User",
            "role": "user"
        })
        if resp.status_code == 400 or resp.status_code == 409:
            record("Auth", "Register", "Duplicate email/phone handled", "PASS", "", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
        else:
            record("Auth", "Register", "Duplicate email/phone handled", "WARNING", f"Got {resp.status_code}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)

    # 1.4 Login with email
    if ctx.access_token:
        resp, elapsed = req("POST", "/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        if resp.status_code == 200:
            record("Auth", "Login", "Login with email+password", "PASS", "", "Critical", elapsed, "/auth/login", "POST", resp.status_code)
        else:
            record("Auth", "Login", "Login with email+password", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/auth/login", "POST", resp.status_code)

    # 1.5 Login with wrong password
    resp, elapsed = req("POST", "/auth/login", json={
        "email": test_email,
        "password": "wrongpassword"
    })
    if resp.status_code == 401:
        record("Auth", "Login", "Invalid credentials rejected", "PASS", "", "Critical", elapsed, "/auth/login", "POST", resp.status_code)
    else:
        record("Auth", "Login", "Invalid credentials rejected", "WARNING", f"Got {resp.status_code}", "Critical", elapsed, "/auth/login", "POST", resp.status_code)

    # 1.6 Get current user
    if ctx.access_token:
        resp, elapsed = req("GET", "/auth/me", headers={"Authorization": f"Bearer {ctx.access_token}"})
        if resp.status_code == 200:
            record("Auth", "Profile", "Get current user", "PASS", "", "Critical", elapsed, "/auth/me", "GET", resp.status_code)
        else:
            record("Auth", "Profile", "Get current user", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/auth/me", "GET", resp.status_code)

    # 1.7 Refresh token
    if ctx.refresh_token:
        resp, elapsed = req("POST", "/auth/refresh", json={"refresh_token": ctx.refresh_token})
        if resp.status_code == 200:
            record("Auth", "Token", "Refresh access token", "PASS", "", "Critical", elapsed, "/auth/refresh", "POST", resp.status_code)
        else:
            record("Auth", "Token", "Refresh access token", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/auth/refresh", "POST", resp.status_code)

    # 1.8 Password reset request
    resp, elapsed = req("POST", "/auth/password-reset-request", json={"email": test_email})
    if resp.status_code in [200, 202]:
        record("Auth", "Password", "Password reset request", "PASS", "", "High", elapsed, "/auth/password-reset-request", "POST", resp.status_code)
    else:
        record("Auth", "Password", "Password reset request", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/auth/password-reset-request", "POST", resp.status_code)

    # 1.9 Change password
    if ctx.access_token:
        resp, elapsed = req("POST", "/auth/change-password", headers={"Authorization": f"Bearer {ctx.access_token}"}, json={
            "current_password": test_password,
            "new_password": "NewPass123!"
        })
        if resp.status_code == 200:
            record("Auth", "Password", "Change password", "PASS", "", "High", elapsed, "/auth/change-password", "POST", resp.status_code)
            # Change it back
            req("POST", "/auth/change-password", headers={"Authorization": f"Bearer {ctx.access_token}"}, json={
                "current_password": "NewPass123!",
                "new_password": test_password
            })
        else:
            record("Auth", "Password", "Change password", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/auth/change-password", "POST", resp.status_code)

    # 1.10 Google OAuth config
    resp, elapsed = req("GET", "/auth/google/config")
    if resp.status_code == 200:
        record("Auth", "OAuth", "Google OAuth config", "PASS", "", "Medium", elapsed, "/auth/google/config", "GET", resp.status_code)
    else:
        record("Auth", "OAuth", "Google OAuth config", "FAIL", f"Status {resp.status_code}", "Medium", elapsed, "/auth/google/config", "GET", resp.status_code)

# ============================================================
# MODULE 2: MAIN PLATFORM (PUBLIC)
# ============================================================
def test_public_platform(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 2: MAIN PLATFORM (PUBLIC)")
    print("="*60)

    # 2.1 Stats
    resp, elapsed = req("GET", "/stats")
    if resp.status_code == 200:
        record("Platform", "Stats", "Get platform stats", "PASS", "", "Medium", elapsed, "/stats", "GET", resp.status_code)
    else:
        record("Platform", "Stats", "Get platform stats", "WARNING", f"Status {resp.status_code}", "Medium", elapsed, "/stats", "GET", resp.status_code)

    # 2.2 Events list
    resp, elapsed = req("GET", "/events")
    if resp.status_code == 200:
        data = resp.json()
        events = data if isinstance(data, list) else data.get("items", [])
        record("Platform", "Events", "List events", "PASS", f"Found {len(events)} events", "Critical", elapsed, "/events", "GET", resp.status_code)
        if events:
            ctx.event_id = events[0].get("id")
    else:
        record("Platform", "Events", "List events", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/events", "GET", resp.status_code)

    # 2.3 Event detail
    if ctx.event_id:
        resp, elapsed = req("GET", f"/events/{ctx.event_id}")
        if resp.status_code == 200:
            record("Platform", "Events", "Get event detail", "PASS", f"Event {ctx.event_id}", "Critical", elapsed, f"/events/{ctx.event_id}", "GET", resp.status_code)
        else:
            record("Platform", "Events", "Get event detail", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, f"/events/{ctx.event_id}", "GET", resp.status_code)

    # 2.4 Venues list (clubs)
    resp, elapsed = req("GET", "/clubs")
    if resp.status_code == 200:
        data = resp.json()
        venues = data if isinstance(data, list) else data.get("items", [])
        record("Platform", "Venues", "List venues/clubs", "PASS", f"Found {len(venues)} venues", "Critical", elapsed, "/clubs", "GET", resp.status_code)
    else:
        record("Platform", "Venues", "List venues/clubs", "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/clubs", "GET", resp.status_code)

    # 2.5 Sports leagues (correct prefix: /sports/leagues)
    resp, elapsed = req("GET", "/sports/leagues")
    if resp.status_code == 200:
        data = resp.json()
        leagues = data if isinstance(data, list) else data.get("items", [])
        record("Platform", "Sports", "List leagues", "PASS", f"Found {len(leagues)} leagues", "Medium", elapsed, "/sports/leagues", "GET", resp.status_code)
    else:
        record("Platform", "Sports", "List leagues", "FAIL", f"Status {resp.status_code}", "Medium", elapsed, "/sports/leagues", "GET", resp.status_code)

    # 2.6 Fixtures (correct prefix: /sports/fixtures)
    resp, elapsed = req("GET", "/sports/fixtures")
    if resp.status_code == 200:
        record("Platform", "Sports", "List fixtures", "PASS", "", "Medium", elapsed, "/sports/fixtures", "GET", resp.status_code)
    else:
        record("Platform", "Sports", "List fixtures", "FAIL", f"Status {resp.status_code}", "Medium", elapsed, "/sports/fixtures", "GET", resp.status_code)

    # 2.7 Music mixes (correct prefix: /music/mixes)
    resp, elapsed = req("GET", "/music/mixes")
    if resp.status_code == 200:
        record("Platform", "Music", "List mixes", "PASS", "", "Low", elapsed, "/music/mixes", "GET", resp.status_code)
    else:
        record("Platform", "Music", "List mixes", "FAIL", f"Status {resp.status_code}", "Low", elapsed, "/music/mixes", "GET", resp.status_code)

    # 2.8 Recaps
    resp, elapsed = req("GET", "/recaps")
    if resp.status_code == 200:
        record("Platform", "Recaps", "List recaps", "PASS", "", "Low", elapsed, "/recaps", "GET", resp.status_code)
    else:
        record("Platform", "Recaps", "List recaps", "FAIL", f"Status {resp.status_code}", "Low", elapsed, "/recaps", "GET", resp.status_code)

    # 2.9 Contact categories
    resp, elapsed = req("GET", "/contact/categories")
    if resp.status_code == 200:
        record("Platform", "Contact", "Get contact categories", "PASS", "", "Medium", elapsed, "/contact/categories", "GET", resp.status_code)
    else:
        record("Platform", "Contact", "Get contact categories", "FAIL", f"Status {resp.status_code}", "Medium", elapsed, "/contact/categories", "GET", resp.status_code)

    # 2.10 Submit contact form
    resp, elapsed = req("POST", "/contact", json={
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Subject",
        "message": "This is a test contact submission with sufficient length."
    })
    if resp.status_code in [200, 201]:
        record("Platform", "Contact", "Submit contact form", "PASS", "", "Medium", elapsed, "/contact", "POST", resp.status_code)
    else:
        record("Platform", "Contact", "Submit contact form", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/contact", "POST", resp.status_code)

# ============================================================
# MODULE 3: PROTECTED USER ENDPOINTS
# ============================================================
def test_user_endpoints(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 3: PROTECTED USER ENDPOINTS")
    print("="*60)

    if not ctx.access_token:
        record("User", "Auth", "User endpoints skipped - no token", "FAIL", "", "Critical", 0, "", "", 0)
        return

    headers = {"Authorization": f"Bearer {ctx.access_token}"}

    # 3.1 Get my tickets
    resp, elapsed = req("GET", "/tickets/user", headers=headers)
    if resp.status_code == 200:
        record("User", "Tickets", "Get my tickets", "PASS", "", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)
    else:
        record("User", "Tickets", "Get my tickets", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)

    # 3.2 Get my orders
    resp, elapsed = req("GET", "/orders/user", headers=headers)
    if resp.status_code == 200:
        record("User", "Orders", "Get my orders", "PASS", "", "Critical", elapsed, "/orders/user", "GET", resp.status_code)
    else:
        record("User", "Orders", "Get my orders", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/orders/user", "GET", resp.status_code)

    # 3.3 Get my events (created)
    resp, elapsed = req("GET", "/events/me", headers=headers)
    if resp.status_code == 200:
        record("User", "Events", "Get my events", "PASS", "", "High", elapsed, "/events/me", "GET", resp.status_code)
    else:
        record("User", "Events", "Get my events", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/events/me", "GET", resp.status_code)

    # 3.4 Get notifications
    resp, elapsed = req("GET", "/notifications", headers=headers)
    if resp.status_code == 200:
        record("User", "Notifications", "Get notifications", "PASS", "", "Medium", elapsed, "/notifications", "GET", resp.status_code)
    else:
        record("User", "Notifications", "Get notifications", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/notifications", "GET", resp.status_code)

    # 3.5 Get notification count
    resp, elapsed = req("GET", "/notifications/count", headers=headers)
    if resp.status_code == 200:
        record("User", "Notifications", "Get notification count", "PASS", "", "Medium", elapsed, "/notifications/count", "GET", resp.status_code)
    else:
        record("User", "Notifications", "Get notification count", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/notifications/count", "GET", resp.status_code)

    # 3.6 Get user settings
    resp, elapsed = req("GET", "/users/me/settings", headers=headers)
    if resp.status_code == 200:
        record("User", "Settings", "Get user settings", "PASS", "", "Medium", elapsed, "/users/me/settings", "GET", resp.status_code)
    else:
        record("User", "Settings", "Get user settings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/users/me/settings", "GET", resp.status_code)

    # 3.7 Update user settings
    resp, elapsed = req("PATCH", "/users/me/settings", headers=headers, json={
        "language": "en",
        "notifications_enabled": True
    })
    if resp.status_code == 200:
        record("User", "Settings", "Update user settings", "PASS", "", "Medium", elapsed, "/users/me/settings", "PATCH", resp.status_code)
    else:
        record("User", "Settings", "Update user settings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/users/me/settings", "PATCH", resp.status_code)

    # 3.8 Get favorites
    resp, elapsed = req("GET", "/favorites/events", headers=headers)
    if resp.status_code == 200:
        record("User", "Favorites", "Get favorite events", "PASS", "", "Low", elapsed, "/favorites/events", "GET", resp.status_code)
    else:
        record("User", "Favorites", "Get favorite events", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Low", elapsed, "/favorites/events", "GET", resp.status_code)

    # 3.9 Cart sync
    resp, elapsed = req("POST", "/cart/sync", headers=headers, json={"items": []})
    if resp.status_code == 200:
        record("User", "Cart", "Sync cart", "PASS", "", "Medium", elapsed, "/cart/sync", "POST", resp.status_code)
    else:
        record("User", "Cart", "Sync cart", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/cart/sync", "POST", resp.status_code)

# ============================================================
# MODULE 4: ADMIN DASHBOARD
# ============================================================
def test_admin(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 4: ADMIN DASHBOARD")
    print("="*60)

    # 4.1 Admin login - uses form data
    resp, elapsed = req("POST", "/admin/auth/login", data={
        "email": "admin",
        "password": "admin123"
    })
    if resp.status_code == 200:
        data = resp.json()
        ctx.admin_token = data.get("access_token") or data.get("token")
        record("Admin", "Auth", "Admin login", "PASS", "", "Critical", elapsed, "/admin/auth/login", "POST", resp.status_code)
    else:
        record("Admin", "Auth", "Admin login", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/admin/auth/login", "POST", resp.status_code)
        return

    headers = {"Authorization": f"Bearer {ctx.admin_token}"}

    # 4.2 Super admin dashboard
    resp, elapsed = req("GET", "/admin/super/dashboard", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Dashboard", "Super admin dashboard", "PASS", "", "Critical", elapsed, "/admin/super/dashboard", "GET", resp.status_code)
    else:
        record("Admin", "Dashboard", "Super admin dashboard", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/admin/super/dashboard", "GET", resp.status_code)

    # 4.3 List users
    resp, elapsed = req("GET", "/admin/users", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        users = data if isinstance(data, list) else data.get("items", [])
        record("Admin", "Users", "List all users", "PASS", f"Found {len(users)} users", "Critical", elapsed, "/admin/users", "GET", resp.status_code)
    else:
        record("Admin", "Users", "List all users", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/admin/users", "GET", resp.status_code)

    # 4.4 Finance transactions
    resp, elapsed = req("GET", "/admin/finance/transactions", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Finance", "List transactions", "PASS", "", "Critical", elapsed, "/admin/finance/transactions", "GET", resp.status_code)
    else:
        record("Admin", "Finance", "List transactions", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/admin/finance/transactions", "GET", resp.status_code)

    # 4.5 Payouts
    resp, elapsed = req("GET", "/admin/finance/payouts", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Finance", "List payouts", "PASS", "", "Critical", elapsed, "/admin/finance/payouts", "GET", resp.status_code)
    else:
        record("Admin", "Finance", "List payouts", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/admin/finance/payouts", "GET", resp.status_code)

    # 4.6 Config
    resp, elapsed = req("GET", "/admin/config", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Config", "Get system config", "PASS", "", "High", elapsed, "/admin/config", "GET", resp.status_code)
    else:
        record("Admin", "Config", "Get system config", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/admin/config", "GET", resp.status_code)

    # 4.7 Verification requests
    resp, elapsed = req("GET", "/admin/verifications", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Verifications", "List verification requests", "PASS", "", "High", elapsed, "/admin/verifications", "GET", resp.status_code)
    else:
        record("Admin", "Verifications", "List verification requests", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/admin/verifications", "GET", resp.status_code)

    # 4.8 Activity logs
    resp, elapsed = req("GET", "/admin/activity-logs", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Audit", "Get activity logs", "PASS", "", "Medium", elapsed, "/admin/activity-logs", "GET", resp.status_code)
    else:
        record("Admin", "Audit", "Get activity logs", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/admin/activity-logs", "GET", resp.status_code)

    # 4.9 Commission rates
    resp, elapsed = req("GET", "/admin/commission-rates", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Finance", "Get commission rates", "PASS", "", "High", elapsed, "/admin/commission-rates", "GET", resp.status_code)
    else:
        record("Admin", "Finance", "Get commission rates", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/admin/commission-rates", "GET", resp.status_code)

    # 4.10 System flags
    resp, elapsed = req("GET", "/admin/system-flags", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Config", "Get system flags", "PASS", "", "Medium", elapsed, "/admin/system-flags", "GET", resp.status_code)
    else:
        record("Admin", "Config", "Get system flags", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/admin/system-flags", "GET", resp.status_code)

    # 4.11 Admin logout
    resp, elapsed = req("POST", "/admin/auth/logout", headers=headers)
    if resp.status_code == 200:
        record("Admin", "Auth", "Admin logout", "PASS", "", "Medium", elapsed, "/admin/auth/logout", "POST", resp.status_code)
    else:
        record("Admin", "Auth", "Admin logout", "WARNING", f"Status {resp.status_code}", "Medium", elapsed, "/admin/auth/logout", "POST", resp.status_code)

# ============================================================
# MODULE 5: ORGANIZER DASHBOARD
# ============================================================
def test_organizer(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 5: ORGANIZER DASHBOARD")
    print("="*60)

    # First register an organizer
    unique = str(uuid.uuid4())[:8]
    org_email = f"organizer_{unique}@example.com"
    org_password = "OrgPass123!"

    resp, elapsed = req("POST", "/auth/register", json={
        "email": org_email,
        "phone": f"+23288{unique}",
        "password": org_password,
        "first_name": "Test",
        "last_name": f"Organizer{unique}",
        "role": "organizer"
    })
    if resp.status_code == 200 or resp.status_code == 201:
        data = resp.json()
        ctx.organizer_token = data.get("access_token")
        record("Organizer", "Auth", "Register organizer", "PASS", "", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
    else:
        record("Organizer", "Auth", "Register organizer", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
        # Try login with a known test user if registration fails
        resp, elapsed = req("POST", "/auth/login", json={"email": org_email, "password": org_password})
        if resp.status_code == 200:
            ctx.organizer_token = resp.json().get("access_token")
        else:
            return

    headers = {"Authorization": f"Bearer {ctx.organizer_token}"}

    # 5.1 Organizer dashboard
    resp, elapsed = req("GET", "/organizer/dashboard", headers=headers)
    if resp.status_code == 200:
        record("Organizer", "Dashboard", "Get organizer dashboard", "PASS", "", "Critical", elapsed, "/organizer/dashboard", "GET", resp.status_code)
    else:
        record("Organizer", "Dashboard", "Get organizer dashboard", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/organizer/dashboard", "GET", resp.status_code)

    # 5.2 Dashboard stats
    resp, elapsed = req("GET", "/organizer/dashboard/stats", headers=headers)
    if resp.status_code == 200:
        record("Organizer", "Dashboard", "Get dashboard stats", "PASS", "", "Critical", elapsed, "/organizer/dashboard/stats", "GET", resp.status_code)
    else:
        record("Organizer", "Dashboard", "Get dashboard stats", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/organizer/dashboard/stats", "GET", resp.status_code)

    # 5.3 List organizer events
    resp, elapsed = req("GET", "/organizer/events", headers=headers)
    if resp.status_code == 200:
        record("Organizer", "Events", "List organizer events", "PASS", "", "Critical", elapsed, "/organizer/events", "GET", resp.status_code)
    else:
        record("Organizer", "Events", "List organizer events", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/organizer/events", "GET", resp.status_code)

    # 5.4 Create event
    event_data = {
        "title": f"Test Event {unique}",
        "description": "A test event for survey",
        "event_type": "concert",
        "start_date": "2026-05-01T18:00:00",
        "end_date": "2026-05-01T23:00:00",
        "city": "Freetown",
        "address": "Test Venue, Freetown",
        "is_public": True,
        "ticket_tiers": [
            {
                "name": "General Admission",
                "price": 50000,
                "quantity": 100,
                "description": "Standard entry"
            }
        ]
    }
    resp, elapsed = req("POST", "/organizer/events", headers=headers, json=event_data)
    if resp.status_code in [200, 201]:
        data = resp.json()
        created_event_id = data.get("id")
        record("Organizer", "Events", "Create event with ticket tiers", "PASS", f"Event ID: {created_event_id}", "Critical", elapsed, "/organizer/events", "POST", resp.status_code)
    else:
        record("Organizer", "Events", "Create event with ticket tiers", "FAIL", f"Status {resp.status_code}: {resp.text[:300]}", "Critical", elapsed, "/organizer/events", "POST", resp.status_code)
        created_event_id = None

    # 5.5 Sales
    resp, elapsed = req("GET", "/organizer/sales", headers=headers)
    if resp.status_code == 200:
        record("Organizer", "Sales", "Get sales data", "PASS", "", "Critical", elapsed, "/organizer/sales", "GET", resp.status_code)
    else:
        record("Organizer", "Sales", "Get sales data", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/organizer/sales", "GET", resp.status_code)

    # 5.6 Payouts
    resp, elapsed = req("GET", "/organizer/payouts", headers=headers)
    if resp.status_code == 200:
        record("Organizer", "Payouts", "Get payouts", "PASS", "", "High", elapsed, "/organizer/payouts", "GET", resp.status_code)
    else:
        record("Organizer", "Payouts", "Get payouts", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/organizer/payouts", "GET", resp.status_code)

    # 5.7 Request payout
    resp, elapsed = req("POST", "/organizer/payouts/request", headers=headers, json={
        "amount": 100000,
        "payment_method": "mobile_money",
        "phone_number": "+23277123456"
    })
    if resp.status_code in [200, 201]:
        record("Organizer", "Payouts", "Request payout", "PASS", "", "High", elapsed, "/organizer/payouts/request", "POST", resp.status_code)
    else:
        record("Organizer", "Payouts", "Request payout", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/organizer/payouts/request", "POST", resp.status_code)

# ============================================================
# MODULE 6: VENUE DASHBOARD
# ============================================================
def test_venue(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 6: VENUE DASHBOARD")
    print("="*60)

    unique = str(uuid.uuid4())[:8]
    venue_email = f"venue_{unique}@example.com"
    venue_password = "VenuePass123!"

    resp, elapsed = req("POST", "/auth/register", json={
        "email": venue_email,
        "phone": f"+23299{unique}",
        "password": venue_password,
        "first_name": "Test",
        "last_name": f"Venue{unique}",
        "role": "venue"
    })
    if resp.status_code == 200 or resp.status_code == 201:
        data = resp.json()
        ctx.venue_token = data.get("access_token")
        record("Venue", "Auth", "Register venue owner", "PASS", "", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
    else:
        record("Venue", "Auth", "Register venue owner", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
        return

    headers = {"Authorization": f"Bearer {ctx.venue_token}"}

    # 6.1 Venue dashboard
    resp, elapsed = req("GET", "/venue/dashboard", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Dashboard", "Get venue dashboard", "PASS", "", "Critical", elapsed, "/venue/dashboard", "GET", resp.status_code)
    else:
        record("Venue", "Dashboard", "Get venue dashboard", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/venue/dashboard", "GET", resp.status_code)

    # 6.2 Venue stats
    resp, elapsed = req("GET", "/venue/dashboard/stats", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Dashboard", "Get venue stats", "PASS", "", "Critical", elapsed, "/venue/dashboard/stats", "GET", resp.status_code)
    else:
        record("Venue", "Dashboard", "Get venue stats", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/venue/dashboard/stats", "GET", resp.status_code)

    # 6.3 Venue events
    resp, elapsed = req("GET", "/venue/events", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Events", "Get venue events", "PASS", "", "High", elapsed, "/venue/events", "GET", resp.status_code)
    else:
        record("Venue", "Events", "Get venue events", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/venue/events", "GET", resp.status_code)

    # 6.4 Venue bookings
    resp, elapsed = req("GET", "/venue/bookings", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Bookings", "Get venue bookings", "PASS", "", "High", elapsed, "/venue/bookings", "GET", resp.status_code)
    else:
        record("Venue", "Bookings", "Get venue bookings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/venue/bookings", "GET", resp.status_code)

    # 6.5 Venue earnings
    resp, elapsed = req("GET", "/venue/earnings", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Earnings", "Get venue earnings", "PASS", "", "High", elapsed, "/venue/earnings", "GET", resp.status_code)
    else:
        record("Venue", "Earnings", "Get venue earnings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/venue/earnings", "GET", resp.status_code)

    # 6.6 Venue settings
    resp, elapsed = req("GET", "/venue/settings", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Settings", "Get venue settings", "PASS", "", "Medium", elapsed, "/venue/settings", "GET", resp.status_code)
    else:
        record("Venue", "Settings", "Get venue settings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/venue/settings", "GET", resp.status_code)

    # 6.7 Venue subscription
    resp, elapsed = req("GET", "/venue/subscription", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Subscription", "Get venue subscription", "PASS", "", "Medium", elapsed, "/venue/subscription", "GET", resp.status_code)
    else:
        record("Venue", "Subscription", "Get venue subscription", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/venue/subscription", "GET", resp.status_code)

    # 6.8 Subscription plans
    resp, elapsed = req("GET", "/venue/subscription/plans", headers=headers)
    if resp.status_code == 200:
        record("Venue", "Subscription", "Get subscription plans", "PASS", "", "Medium", elapsed, "/venue/subscription/plans", "GET", resp.status_code)
    else:
        record("Venue", "Subscription", "Get subscription plans", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/venue/subscription/plans", "GET", resp.status_code)

# ============================================================
# MODULE 7: SPORTS DASHBOARD
# ============================================================
def test_sports(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 7: SPORTS DASHBOARD")
    print("="*60)

    unique = str(uuid.uuid4())[:8]
    sports_email = f"sports_{unique}@example.com"
    sports_password = "SportsPass123!"

    resp, elapsed = req("POST", "/auth/register", json={
        "email": sports_email,
        "phone": f"+23266{unique}",
        "password": sports_password,
        "first_name": "Test",
        "last_name": f"Sports{unique}",
        "role": "sport"
    })
    if resp.status_code == 200 or resp.status_code == 201:
        data = resp.json()
        ctx.sports_token = data.get("access_token")
        record("Sports", "Auth", "Register sports facility", "PASS", "", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
    else:
        record("Sports", "Auth", "Register sports facility", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/auth/register", "POST", resp.status_code)
        return

    headers = {"Authorization": f"Bearer {ctx.sports_token}"}

    # 7.1 Sports dashboard
    resp, elapsed = req("GET", "/sports/dashboard", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Dashboard", "Get sports dashboard", "PASS", "", "Critical", elapsed, "/sports/dashboard", "GET", resp.status_code)
    else:
        record("Sports", "Dashboard", "Get sports dashboard", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/sports/dashboard", "GET", resp.status_code)

    # 7.2 Sports stats
    resp, elapsed = req("GET", "/sports/dashboard/stats", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Dashboard", "Get sports stats", "PASS", "", "Critical", elapsed, "/sports/dashboard/stats", "GET", resp.status_code)
    else:
        record("Sports", "Dashboard", "Get sports stats", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/sports/dashboard/stats", "GET", resp.status_code)

    # 7.3 Courts
    resp, elapsed = req("GET", "/sports/courts", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Courts", "List courts", "PASS", "", "Critical", elapsed, "/sports/courts", "GET", resp.status_code)
    else:
        record("Sports", "Courts", "List courts", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/sports/courts", "GET", resp.status_code)

    # 7.4 Create court
    resp, elapsed = req("POST", "/sports/courts", headers=headers, json={
        "name": f"Court {unique}",
        "sport_type": "football",
        "surface_type": "grass",
        "capacity": 22,
        "hourly_rate": 50000,
        "is_active": True
    })
    if resp.status_code in [200, 201]:
        record("Sports", "Courts", "Create court", "PASS", "", "Critical", elapsed, "/sports/courts", "POST", resp.status_code)
    else:
        record("Sports", "Courts", "Create court", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/sports/courts", "POST", resp.status_code)

    # 7.5 Bookings
    resp, elapsed = req("GET", "/sports/bookings", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Bookings", "List sports bookings", "PASS", "", "High", elapsed, "/sports/bookings", "GET", resp.status_code)
    else:
        record("Sports", "Bookings", "List sports bookings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/sports/bookings", "GET", resp.status_code)

    # 7.6 Earnings
    resp, elapsed = req("GET", "/sports/earnings", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Earnings", "Get sports earnings", "PASS", "", "High", elapsed, "/sports/earnings", "GET", resp.status_code)
    else:
        record("Sports", "Earnings", "Get sports earnings", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/sports/earnings", "GET", resp.status_code)

    # 7.7 Subscription
    resp, elapsed = req("GET", "/sports/subscription", headers=headers)
    if resp.status_code == 200:
        record("Sports", "Subscription", "Get sports subscription", "PASS", "", "Medium", elapsed, "/sports/subscription", "GET", resp.status_code)
    else:
        record("Sports", "Subscription", "Get sports subscription", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/sports/subscription", "GET", resp.status_code)

# ============================================================
# MODULE 8: PAYMENTS
# ============================================================
def test_payments(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 8: PAYMENTS")
    print("="*60)

    if not ctx.access_token:
        record("Payments", "Auth", "Payment tests skipped - no user token", "FAIL", "", "Critical", 0, "", "", 0)
        return

    headers = {"Authorization": f"Bearer {ctx.access_token}"}

    # 8.1 Get payment methods
    resp, elapsed = req("GET", "/payments/methods", headers=headers)
    if resp.status_code == 200:
        record("Payments", "Methods", "Get payment methods", "PASS", "", "Critical", elapsed, "/payments/methods", "GET", resp.status_code)
    else:
        record("Payments", "Methods", "Get payment methods", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/payments/methods", "GET", resp.status_code)

    # 8.2 Create order - need an event with ticket tiers
    resp, elapsed = req("GET", "/events")
    if resp.status_code == 200:
        events = resp.json()
        if isinstance(events, list) and len(events) > 0:
            event = events[0]
            event_id = event.get("id")
            # Get ticket tiers
            resp2, _ = req("GET", f"/events/{event_id}/ticket-tiers")
            tiers = resp2.json() if resp2.status_code == 200 else []
            if tiers:
                tier_id = tiers[0].get("id")
                resp3, elapsed3 = req("POST", "/payments/orders", headers=headers, json={
                    "event_id": event_id,
                    "items": [{"ticket_tier_id": tier_id, "quantity": 1}]
                })
                if resp3.status_code in [200, 201]:
                    ctx.order_id = resp3.json().get("id")
                    record("Payments", "Orders", "Create order", "PASS", f"Order ID: {ctx.order_id}", "Critical", elapsed3, "/payments/orders", "POST", resp3.status_code)
                else:
                    record("Payments", "Orders", "Create order", "FAIL", f"Status {resp3.status_code}: {resp3.text[:200]}", "Critical", elapsed3, "/payments/orders", "POST", resp3.status_code)
            else:
                record("Payments", "Orders", "Create order", "FAIL", "No ticket tiers found", "Critical", 0, "/payments/orders", "POST", 0)
        else:
            record("Payments", "Orders", "Create order", "FAIL", "No events found", "Critical", 0, "/payments/orders", "POST", 0)
    else:
        record("Payments", "Orders", "Create order", "FAIL", "Could not fetch events", "Critical", 0, "/payments/orders", "POST", 0)

    # 8.3 Orange Money initiate
    resp, elapsed = req("POST", "/orange-money/initiate", headers=headers, json={
        "order_id": ctx.order_id or 1,
        "phone_number": "+23277123456"
    })
    if resp.status_code in [200, 201, 202]:
        record("Payments", "Orange Money", "Initiate payment", "PASS", "", "Critical", elapsed, "/orange-money/initiate", "POST", resp.status_code)
    else:
        record("Payments", "Orange Money", "Initiate payment", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/orange-money/initiate", "POST", resp.status_code)

    # 8.4 Monime checkout
    resp, elapsed = req("POST", "/monime/checkout/initiate", headers=headers, json={
        "amount": 50000,
        "currency": "SLL",
        "description": "Test payment"
    })
    if resp.status_code in [200, 201, 202]:
        record("Payments", "Monime", "Initiate checkout", "PASS", "", "Critical", elapsed, "/monime/checkout/initiate", "POST", resp.status_code)
    else:
        record("Payments", "Monime", "Initiate checkout", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/monime/checkout/initiate", "POST", resp.status_code)

    # 8.5 Stripe create intent
    resp, elapsed = req("POST", "/payments/create-intent", headers=headers, json={
        "amount": 50000,
        "currency": "sll"
    })
    if resp.status_code in [200, 201]:
        record("Payments", "Stripe", "Create payment intent", "PASS", "", "High", elapsed, "/payments/create-intent", "POST", resp.status_code)
    else:
        record("Payments", "Stripe", "Create payment intent", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "High", elapsed, "/payments/create-intent", "POST", resp.status_code)

# ============================================================
# MODULE 9: TICKETS & QR
# ============================================================
def test_tickets(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 9: TICKETS & QR")
    print("="*60)

    # 9.1 Validate ticket by number (requires organizer auth)
    resp, elapsed = req("GET", "/tickets/validate/TEST123")
    if resp.status_code == 401:
        record("Tickets", "Validation", "Ticket validate requires auth", "PASS", "Protected endpoint", "Critical", elapsed, "/tickets/validate/:number", "GET", resp.status_code)
    elif resp.status_code == 403:
        record("Tickets", "Validation", "Ticket validate requires organizer", "PASS", "Role protected", "Critical", elapsed, "/tickets/validate/:number", "GET", resp.status_code)
    else:
        record("Tickets", "Validation", "Ticket validate behavior", "WARNING", f"Unexpected {resp.status_code}", "Critical", elapsed, "/tickets/validate/:number", "GET", resp.status_code)

    # 9.2 QR validate (requires organizer auth)
    resp, elapsed = req("POST", "/qr/validate", json={"qr_token": "test_token"})
    if resp.status_code == 401:
        record("Tickets", "Validation", "QR validate requires auth", "PASS", "Protected endpoint", "Critical", elapsed, "/qr/validate", "POST", resp.status_code)
    else:
        record("Tickets", "Validation", "QR validate behavior", "WARNING", f"Unexpected {resp.status_code}", "Critical", elapsed, "/qr/validate", "POST", resp.status_code)

    # 9.3 Ticket lookup by token (requires auth)
    resp, elapsed = req("GET", "/payments/tickets/lookup/test_token")
    if resp.status_code == 401:
        record("Tickets", "Lookup", "Ticket lookup requires auth", "PASS", "Protected endpoint", "High", elapsed, "/payments/tickets/lookup/:token", "GET", resp.status_code)
    else:
        record("Tickets", "Lookup", "Ticket lookup behavior", "WARNING", f"Unexpected {resp.status_code}", "High", elapsed, "/payments/tickets/lookup/:token", "GET", resp.status_code)

# ============================================================
# MODULE 10: SUBSCRIPTIONS
# ============================================================
def test_subscriptions(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 10: SUBSCRIPTIONS")
    print("="*60)

    # 10.1 Public subscription plans (correct prefix: /subscriptions/plans)
    resp, elapsed = req("GET", "/subscriptions/plans")
    if resp.status_code == 200:
        record("Subscriptions", "Plans", "Get public subscription plans", "PASS", "", "Medium", elapsed, "/subscriptions/plans", "GET", resp.status_code)
    else:
        record("Subscriptions", "Plans", "Get public subscription plans", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/subscriptions/plans", "GET", resp.status_code)

    # 10.2 My subscription (needs auth)
    if ctx.access_token:
        headers = {"Authorization": f"Bearer {ctx.access_token}"}
        resp, elapsed = req("GET", "/subscriptions/my", headers=headers)
        if resp.status_code == 200:
            record("Subscriptions", "My Plan", "Get my subscription", "PASS", "", "Medium", elapsed, "/subscriptions/my", "GET", resp.status_code)
        else:
            record("Subscriptions", "My Plan", "Get my subscription", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/subscriptions/my", "GET", resp.status_code)

        resp, elapsed = req("GET", "/subscriptions/transactions", headers=headers)
        if resp.status_code == 200:
            record("Subscriptions", "Transactions", "Get subscription transactions", "PASS", "", "Medium", elapsed, "/subscriptions/transactions", "GET", resp.status_code)
        else:
            record("Subscriptions", "Transactions", "Get subscription transactions", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Medium", elapsed, "/subscriptions/transactions", "GET", resp.status_code)

# ============================================================
# MODULE 11: SECURITY TESTS
# ============================================================
def test_security(ctx: TestContext):
    print("\n" + "="*60)
    print("MODULE 11: SECURITY")
    print("="*60)

    # 11.1 No auth on protected endpoint
    resp, elapsed = req("GET", "/tickets/user")
    if resp.status_code == 401:
        record("Security", "Auth", "Protected endpoint rejects no-auth", "PASS", "", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)
    else:
        record("Security", "Auth", "Protected endpoint rejects no-auth", "FAIL", f"Got {resp.status_code}", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)

    # 11.2 Invalid token
    resp, elapsed = req("GET", "/tickets/user", headers={"Authorization": "Bearer invalidtoken123"})
    if resp.status_code == 401:
        record("Security", "Auth", "Invalid token rejected", "PASS", "", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)
    else:
        record("Security", "Auth", "Invalid token rejected", "FAIL", f"Got {resp.status_code}", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)

    # 11.3 Malformed token
    resp, elapsed = req("GET", "/tickets/user", headers={"Authorization": "NotBearer token"})
    if resp.status_code == 401:
        record("Security", "Auth", "Malformed auth header rejected", "PASS", "", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)
    else:
        record("Security", "Auth", "Malformed auth header rejected", "FAIL", f"Got {resp.status_code}", "Critical", elapsed, "/tickets/user", "GET", resp.status_code)

    # 11.4 User cannot access admin
    if ctx.access_token:
        resp, elapsed = req("GET", "/admin/users", headers={"Authorization": f"Bearer {ctx.access_token}"})
        if resp.status_code == 403 or resp.status_code == 401:
            record("Security", "RBAC", "Regular user blocked from admin", "PASS", f"Status {resp.status_code}", "Critical", elapsed, "/admin/users", "GET", resp.status_code)
        else:
            record("Security", "RBAC", "Regular user blocked from admin", "FAIL", f"Got {resp.status_code}", "Critical", elapsed, "/admin/users", "GET", resp.status_code)

    # 11.5 SQL injection attempt
    resp, elapsed = req("GET", "/events?id=1' OR '1'='1")
    record("Security", "Input", "SQL injection in query param", "PASS" if resp.status_code != 500 else "FAIL", f"Status {resp.status_code}", "Critical", elapsed, "/events?id=...", "GET", resp.status_code)

    # 11.6 XSS attempt in contact form
    resp, elapsed = req("POST", "/contact", json={
        "name": "<script>alert('xss')</script>",
        "email": "test@example.com",
        "subject": "Test XSS subject",
        "message": "<img src=x onerror=alert('xss')> test message here"
    })
    if resp.status_code in [200, 201, 400]:
        record("Security", "Input", "XSS in contact form handled", "PASS", f"Status {resp.status_code}", "Critical", elapsed, "/contact", "POST", resp.status_code)
    else:
        record("Security", "Input", "XSS in contact form handled", "FAIL", f"Status {resp.status_code}: {resp.text[:200]}", "Critical", elapsed, "/contact", "POST", resp.status_code)

# ============================================================
# MAIN
# ============================================================
def main():
    print("="*60)
    print("SOUND IT SALONE - PRODUCTION SURVEY")
    print("API Endpoint Testing")
    print("="*60)

    ctx = TestContext()

    test_auth(ctx)
    test_public_platform(ctx)
    test_user_endpoints(ctx)
    test_admin(ctx)
    test_organizer(ctx)
    test_venue(ctx)
    test_sports(ctx)
    test_payments(ctx)
    test_tickets(ctx)
    test_subscriptions(ctx)
    test_security(ctx)

    # Summary
    print("\n" + "="*60)
    print("SURVEY SUMMARY")
    print("="*60)

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    warnings = sum(1 for r in RESULTS if r["status"] == "WARNING")
    na = sum(1 for r in RESULTS if r["status"] == "N/A")

    print(f"Total Tests:    {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failed}")
    print(f"Warnings:       {warnings}")
    print(f"Not Applicable: {na}")

    # Save results
    with open("/Users/djfredmax/Desktop/SOUND IT SALONE/survey-results.json", "w") as f:
        json.dump(RESULTS, f, indent=2)

    # Save CSV
    import csv
    with open("/Users/djfredmax/Desktop/SOUND IT SALONE/survey-results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["module", "feature", "test_case", "status", "notes", "priority", "response_time_ms", "endpoint", "method", "status_code", "timestamp"])
        writer.writeheader()
        writer.writerows(RESULTS)

    print("\nResults saved to survey-results.json and survey-results.csv")

    # Critical failures
    critical_fails = [r for r in RESULTS if r["status"] == "FAIL" and r["priority"] == "Critical"]
    if critical_fails:
        print(f"\n❌ CRITICAL FAILURES ({len(critical_fails)}):")
        for r in critical_fails:
            print(f"  - [{r['module']}] {r['feature']}: {r['test_case']} — {r['notes']}")

if __name__ == "__main__":
    main()
