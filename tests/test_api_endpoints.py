"""Test all API endpoints."""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


class APITester:
    def __init__(self):
        self.results = []
        self.token = None
    
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
        
        # Register (may fail if user exists)
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test_new@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        })
        self.log("POST", "/auth/register", resp.status_code, resp.status_code in [200, 201, 409])
        
        # Login
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        passed = resp.status_code == 200
        self.log("POST", "/auth/login", resp.status_code, passed)
        
        if passed:
            self.token = resp.json().get("access_token")
        
        # Request password reset
        resp = requests.post(f"{BASE_URL}/auth/password-reset-request", json={
            "email": "test@example.com"
        })
        self.log("POST", "/auth/password-reset-request", resp.status_code, resp.status_code in [200, 202])
        
        # Refresh token (if we have one)
        if self.token:
            resp = requests.post(f"{BASE_URL}/auth/refresh", headers={
                "Authorization": f"Bearer {self.token}"
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
                self.log(f"GET", f"/events/{event_id}", resp.status_code, resp.status_code == 200)
                
                # Get tickets for event
                resp = requests.get(f"{BASE_URL}/events/{event_id}/tickets")
                self.log(f"GET", f"/events/{event_id}/tickets", resp.status_code, resp.status_code == 200)
        
        # Categories
        resp = requests.get(f"{BASE_URL}/events/categories")
        self.log("GET", "/events/categories", resp.status_code, resp.status_code == 200)
        
        # Follow event (if authenticated)
        if self.token and data.get("items"):
            event_id = data["items"][0]["id"]
            resp = requests.post(f"{BASE_URL}/events/{event_id}/follow", headers=headers)
            self.log(f"POST", f"/events/{event_id}/follow", resp.status_code, resp.status_code in [200, 201, 401, 409])
    
    def test_venues(self):
        """Test venue endpoints."""
        print("\n🏢 Testing Venue Endpoints...")
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
        # List venues
        resp = requests.get(f"{BASE_URL}/venues?page=1&page_size=10")
        self.log("GET", "/venues", resp.status_code, resp.status_code == 200)
        
        # Get venue by ID
        if resp.status_code == 200:
            data = resp.json()
            if data.get("items"):
                venue_id = data["items"][0]["id"]
                resp = requests.get(f"{BASE_URL}/venues/{venue_id}")
                self.log(f"GET", f"/venues/{venue_id}", resp.status_code, resp.status_code == 200)
                
                # Get venue events
                resp = requests.get(f"{BASE_URL}/venues/{venue_id}/events")
                self.log(f"GET", f"/venues/{venue_id}/events", resp.status_code, resp.status_code == 200)
        
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
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
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
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
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
        
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        
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
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
    
    tester.print_summary()


if __name__ == "__main__":
    main()
