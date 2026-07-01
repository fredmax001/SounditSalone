"""Test all API endpoints."""
import os
import requests
import sqlite3

BASE_URL = "http://localhost:8000/api/v1"


def _get_latest_otp_code(identifier: str) -> str | None:
    """Fetch the latest unused OTP code from the local SQLite database."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./soundit_local.db")
    db_path = db_url.replace("sqlite:///./", "")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT code FROM otp_codes WHERE identifier = ? AND is_used = 0 ORDER BY created_at DESC LIMIT 1",
            (identifier,),
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


class APITester:
    def __init__(self):
        self.results = []
        self.token = None
        self.refresh_token = None
    
    def log(self, method, endpoint, status, passed):
        status_icon = "✅" if passed else "❌"
        print(f"  {status_icon} {method} {endpoint} - {status}")
        self.results.append({
            "method": method,
            "endpoint": endpoint,
            "status": status,
            "passed": passed
        })
    
    def test_health(self):
        """Test health endpoint."""
        print("\n🩺 Testing Health Endpoints...")
        
        # Basic health
        resp = requests.get(f"{BASE_URL}/health")
        self.log("GET", "/health", resp.status_code, resp.status_code == 200)
        
        # Detailed health
        resp = requests.get(f"{BASE_URL}/health/detailed")
        self.log("GET", "/health/detailed", resp.status_code, resp.status_code == 200)
    
    def test_auth(self):
        """Test auth endpoints."""
        print("\n🔐 Testing Auth Endpoints...")
        
        # Register requires a valid OTP. Request OTP first, then read the code
        # from the local database and complete registration.
        email = "test_new@example.com"
        requests.post(f"{BASE_URL}/otp/email/send", json={
            "email": email,
            "purpose": "register"
        })
        otp_code = _get_latest_otp_code(email)

        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "otp_code": otp_code or "000000"
        })
        self.log("POST", "/auth/register", resp.status_code, resp.status_code in [200, 201, 409])
        
        # Login with the registered user
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": "TestPass123!"
        })
        passed = resp.status_code == 200
        self.log("POST", "/auth/login", resp.status_code, passed)

        if passed:
            self.token = resp.json().get("access_token")
            self.refresh_token = resp.json().get("refresh_token")

        # Request password reset
        resp = requests.post(f"{BASE_URL}/auth/password-reset-request", json={
            "email": email
        })
        self.log("POST", "/auth/password-reset-request", resp.status_code, resp.status_code in [200, 202])

        # Refresh token rotation (if we have a refresh token)
        if getattr(self, "refresh_token", None):
            resp = requests.post(f"{BASE_URL}/auth/refresh", json={
                "refresh_token": self.refresh_token
            })
            self.log("POST", "/auth/refresh", resp.status_code, resp.status_code == 200)
    
    def test_events(self):
        """Test event endpoints."""
        print("\n📅 Testing Event Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # List events
        resp = requests.get(f"{BASE_URL}/events?page=1&page_size=10")
        self.log("GET", "/events", resp.status_code, resp.status_code == 200)
        
        # Search events
        resp = requests.get(f"{BASE_URL}/events/search?query=test")
        self.log("GET", "/events/search", resp.status_code, resp.status_code == 200)
        
        # Get event by ID (if events exist)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("items"):
                event_id = data["items"][0]["id"]
                resp = requests.get(f"{BASE_URL}/events/{event_id}")
                self.log("GET", f"/events/{event_id}", resp.status_code, resp.status_code == 200)
                
                # Get tickets for event
                resp = requests.get(f"{BASE_URL}/events/{event_id}/tickets")
                self.log("GET", f"/events/{event_id}/tickets", resp.status_code, resp.status_code == 200)
        
        # Categories
        resp = requests.get(f"{BASE_URL}/events/categories")
        self.log("GET", "/events/categories", resp.status_code, resp.status_code == 200)
        
        # Follow event (if authenticated)
        if self.token and data.get("items"):
            event_id = data["items"][0]["id"]
            resp = requests.post(f"{BASE_URL}/events/{event_id}/follow", headers=headers)
            self.log("POST", f"/events/{event_id}/follow", resp.status_code, resp.status_code in [200, 201, 401, 409])
    
    def test_venues(self):
        """Test venue endpoints."""
        print("\n🏢 Testing Venue Endpoints...")
        
        # List venues
        resp = requests.get(f"{BASE_URL}/venues?page=1&page_size=10")
        self.log("GET", "/venues", resp.status_code, resp.status_code == 200)
        
        # Get venue by ID
        if resp.status_code == 200:
            data = resp.json()
            if data.get("items"):
                venue_id = data["items"][0]["id"]
                resp = requests.get(f"{BASE_URL}/venues/{venue_id}")
                self.log("GET", f"/venues/{venue_id}", resp.status_code, resp.status_code == 200)
                
                # Get venue events
                resp = requests.get(f"{BASE_URL}/venues/{venue_id}/events")
                self.log("GET", f"/venues/{venue_id}/events", resp.status_code, resp.status_code == 200)
        
        # Categories
        resp = requests.get(f"{BASE_URL}/venues/categories")
        self.log("GET", "/venues/categories", resp.status_code, resp.status_code == 200)
    
    def test_tickets(self):
        """Test ticket endpoints."""
        print("\n🎫 Testing Ticket Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get user tickets (requires auth)
        resp = requests.get(f"{BASE_URL}/tickets/user", headers=headers)
        self.log("GET", "/tickets/user", resp.status_code, resp.status_code in [200, 401])
    
    def test_orders(self):
        """Test order endpoints."""
        print("\n📦 Testing Order Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get user orders (requires auth)
        resp = requests.get(f"{BASE_URL}/orders/user", headers=headers)
        self.log("GET", "/orders/user", resp.status_code, resp.status_code in [200, 401])
    
    def test_sports(self):
        """Test sports endpoints."""
        print("\n⚽ Testing Sports Endpoints...")
        
        # Get leagues
        resp = requests.get(f"{BASE_URL}/sports/leagues")
        self.log("GET", "/sports/leagues", resp.status_code, resp.status_code == 200)
        
        # Get teams
        resp = requests.get(f"{BASE_URL}/sports/teams?page=1&page_size=10")
        self.log("GET", "/sports/teams", resp.status_code, resp.status_code == 200)
        
        # Get facilities
        resp = requests.get(f"{BASE_URL}/sports/facilities?page=1&page_size=10")
        self.log("GET", "/sports/facilities", resp.status_code, resp.status_code == 200)
    
    def test_business(self):
        """Test business endpoints."""
        print("\n💼 Testing Business Endpoints...")
        
        # Get directory
        resp = requests.get(f"{BASE_URL}/business/directory?page=1&page_size=10")
        self.log("GET", "/business/directory", resp.status_code, resp.status_code == 200)
        
        # Categories
        resp = requests.get(f"{BASE_URL}/business/categories")
        self.log("GET", "/business/categories", resp.status_code, resp.status_code == 200)
    
    def test_notifications(self):
        """Test notification endpoints."""
        print("\n🔔 Testing Notification Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get notifications (requires auth)
        resp = requests.get(f"{BASE_URL}/notifications", headers=headers)
        self.log("GET", "/notifications", resp.status_code, resp.status_code in [200, 401])
    
    def test_contact(self):
        """Test contact endpoints."""
        print("\n📧 Testing Contact Endpoints...")
        
        # Submit contact form
        resp = requests.post(f"{BASE_URL}/contact", json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        })
        self.log("POST", "/contact", resp.status_code, resp.status_code in [200, 201])
    
    def test_recaps(self):
        """Test recap endpoints."""
        print("\n📰 Testing Recap Endpoints...")
        
        # Get recaps
        resp = requests.get(f"{BASE_URL}/recaps?page=1&page_size=10")
        self.log("GET", "/recaps", resp.status_code, resp.status_code == 200)
        
        # Search recaps
        resp = requests.get(f"{BASE_URL}/recaps/search?query=test")
        self.log("GET", "/recaps/search", resp.status_code, resp.status_code == 200)
    
    def test_otp(self):
        """Test OTP endpoints."""
        print("\n🔢 Testing OTP Endpoints...")
        
        # Send email OTP
        resp = requests.post(f"{BASE_URL}/otp/email/send", json={
            "email": "test@example.com"
        })
        self.log("POST", "/otp/email/send", resp.status_code, resp.status_code in [200, 202, 429])
        
        # Verify OTP (with dummy code)
        resp = requests.post(f"{BASE_URL}/otp/verify", json={
            "identifier": "test@example.com",
            "code": "000000"
        })
        self.log("POST", "/otp/verify", resp.status_code, resp.status_code in [200, 400, 401])
    
    def test_bookings(self):
        """Test booking endpoints."""
        print("\n📅 Testing Booking Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get user bookings (requires auth)
        resp = requests.get(f"{BASE_URL}/bookings", headers=headers)
        self.log("GET", "/bookings", resp.status_code, resp.status_code in [200, 401])
    
    def test_restaurant_dashboard(self):
        """Test restaurant dashboard endpoints."""
        print("\n🍽️ Testing Restaurant Dashboard Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Dashboard overview (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/dashboard", headers=headers)
        self.log("GET", "/restaurant/dashboard", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Reservations (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/reservations", headers=headers)
        self.log("GET", "/restaurant/reservations", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Orders (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/orders", headers=headers)
        self.log("GET", "/restaurant/orders", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Earnings (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/earnings", headers=headers)
        self.log("GET", "/restaurant/earnings", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Settings (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/settings", headers=headers)
        self.log("GET", "/restaurant/settings", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Reviews (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/reviews", headers=headers)
        self.log("GET", "/restaurant/reviews", resp.status_code, resp.status_code in [200, 401, 403])
        
        # Subscription (requires restaurant role)
        resp = requests.get(f"{BASE_URL}/restaurant/subscription", headers=headers)
        self.log("GET", "/restaurant/subscription", resp.status_code, resp.status_code in [200, 401, 403])
    
    def test_restaurant_reservations(self):
        """Test restaurant reservation endpoints."""
        print("\n🪑 Testing Restaurant Reservation Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get user reservations (requires auth)
        resp = requests.get(f"{BASE_URL}/restaurants/reservations", headers=headers)
        self.log("GET", "/restaurants/reservations", resp.status_code, resp.status_code in [200, 401])
        
        # Get food spots list (public)
        resp = requests.get(f"{BASE_URL}/foodspots")
        self.log("GET", "/foodspots", resp.status_code, resp.status_code == 200)
        
        # Search food spots (public)
        resp = requests.get(f"{BASE_URL}/foodspots/search?q=test")
        self.log("GET", "/foodspots/search", resp.status_code, resp.status_code == 200)
        
        # Get food spot by ID (public)
        spots = requests.get(f"{BASE_URL}/foodspots").json()
        if spots and len(spots) > 0:
            spot_id = spots[0]["id"]
            resp = requests.get(f"{BASE_URL}/foodspots/{spot_id}")
            self.log("GET", f"/foodspots/{spot_id}", resp.status_code, resp.status_code == 200)
            
            # Get food spot reviews (public)
            resp = requests.get(f"{BASE_URL}/foodspots/{spot_id}/reviews")
            self.log("GET", f"/foodspots/{spot_id}/reviews", resp.status_code, resp.status_code == 200)
            
            # Create review (requires auth)
            resp = requests.post(
                f"{BASE_URL}/foodspots/{spot_id}/reviews",
                json={"rating": 5, "comment": "Test review"},
                headers=headers
            )
            self.log("POST", f"/foodspots/{spot_id}/reviews", resp.status_code, resp.status_code in [200, 201, 401])
    
    def test_food_orders(self):
        """Test food ordering endpoints."""
        print("\n🥡 Testing Food Order Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get user food orders (requires auth)
        resp = requests.get(f"{BASE_URL}/restaurants/orders/user", headers=headers)
        self.log("GET", "/restaurants/orders/user", resp.status_code, resp.status_code in [200, 401])
        
        # Create food order (requires auth + valid food spot)
        spots = requests.get(f"{BASE_URL}/foodspots").json()
        if spots and len(spots) > 0:
            spot_id = spots[0]["id"]
            resp = requests.post(
                f"{BASE_URL}/restaurants/orders",
                json={
                    "food_spot_id": spot_id,
                    "items": [{"menu_item_name": "Test Item", "quantity": 1, "price": 50}],
                    "order_type": "dine_in"
                },
                headers=headers
            )
            self.log("POST", "/restaurants/orders", resp.status_code, resp.status_code in [200, 201, 401])
    
    def test_club_reviews(self):
        """Test club review endpoints."""
        print("\n⭐ Testing Club Review Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # Get clubs list (public)
        resp = requests.get(f"{BASE_URL}/clubs")
        self.log("GET", "/clubs", resp.status_code, resp.status_code == 200)
        
        clubs = resp.json() if resp.status_code == 200 else []
        if clubs and len(clubs) > 0:
            club_id = clubs[0]["id"]
            
            # Get club reviews (public)
            resp = requests.get(f"{BASE_URL}/clubs/{club_id}/reviews")
            self.log("GET", f"/clubs/{club_id}/reviews", resp.status_code, resp.status_code == 200)
            
            # Create club review (requires auth)
            resp = requests.post(
                f"{BASE_URL}/clubs/{club_id}/reviews",
                json={"rating": 4, "comment": "Great vibe!"},
                headers=headers
            )
            self.log("POST", f"/clubs/{club_id}/reviews", resp.status_code, resp.status_code in [200, 201, 401])
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"])
        
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {passed/len(self.results)*100:.1f}%" if self.results else "N/A")
        
        if failed > 0:
            print("\nFailed Tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  ❌ {r['method']} {r['endpoint']} - {r['status']}")


def main():
    """Run all API tests."""
    print("=" * 60)
    print("API ENDPOINT TESTS")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    
    tester = APITester()
    
    try:
        tester.test_health()
        tester.test_auth()
        tester.test_events()
        tester.test_venues()
        tester.test_tickets()
        tester.test_orders()
        tester.test_sports()
        tester.test_business()
        tester.test_notifications()
        tester.test_contact()
        tester.test_recaps()
        tester.test_otp()
        tester.test_bookings()
        tester.test_restaurant_dashboard()
        tester.test_restaurant_reservations()
        tester.test_food_orders()
        tester.test_club_reviews()
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
    
    tester.print_summary()


if __name__ == "__main__":
    main()
