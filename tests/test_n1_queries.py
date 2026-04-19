"""Test N+1 query fixes."""
import time
import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_tickets_endpoint():
    """Test that tickets endpoint uses eager loading."""
    print("Testing tickets endpoint for N+1 queries...")
    
    url = f"{BASE_URL}/tickets/user"
    
    # First, we need to login
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    if login_resp.status_code != 200:
        print(f"  Login failed: {login_resp.status_code}")
        print("  Skipping test - need valid credentials")
        return None
    
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    response = requests.get(url, headers=headers)
    duration = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Duration: {duration:.3f}s")
    
    if response.status_code == 200:
        if duration < 1.0:
            print("  ✅ Fast response - likely no N+1 queries\n")
            return True
        else:
            print("  ⚠️  Slow response - might have N+1 queries\n")
            return False
    else:
        print(f"  ❌ Request failed\n")
        return False


def test_orders_endpoint():
    """Test that orders endpoint uses eager loading."""
    print("Testing orders endpoint for N+1 queries...")
    
    url = f"{BASE_URL}/orders/user"
    
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    if login_resp.status_code != 200:
        print(f"  Login failed: {login_resp.status_code}")
        print("  Skipping test - need valid credentials")
        return None
    
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    response = requests.get(url, headers=headers)
    duration = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Duration: {duration:.3f}s")
    
    if response.status_code == 200:
        if duration < 1.0:
            print("  ✅ Fast response - likely no N+1 queries\n")
            return True
        else:
            print("  ⚠️  Slow response - might have N+1 queries\n")
            return False
    else:
        print(f"  ❌ Request failed\n")
        return False


def test_events_list():
    """Test that events list uses eager loading."""
    print("Testing events list for N+1 queries...")
    
    url = f"{BASE_URL}/events?page=1&page_size=20"
    
    start_time = time.time()
    response = requests.get(url)
    duration = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Duration: {duration:.3f}s")
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            print(f"  Items returned: {len(data['items'])}")
        
        if duration < 1.0:
            print("  ✅ Fast response - likely no N+1 queries\n")
            return True
        else:
            print("  ⚠️  Slow response - might have N+1 queries\n")
            return False
    else:
        print(f"  ❌ Request failed\n")
        return False


def test_venues_list():
    """Test that venues list uses eager loading."""
    print("Testing venues list for N+1 queries...")
    
    url = f"{BASE_URL}/venues?page=1&page_size=20"
    
    start_time = time.time()
    response = requests.get(url)
    duration = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Duration: {duration:.3f}s")
    
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            print(f"  Items returned: {len(data['items'])}")
        
        if duration < 1.0:
            print("  ✅ Fast response - likely no N+1 queries\n")
            return True
        else:
            print("  ⚠️  Slow response - might have N+1 queries\n")
            return False
    else:
        print(f"  ❌ Request failed\n")
        return False


def test_event_detail():
    """Test that event detail uses eager loading."""
    print("Testing event detail for N+1 queries...")
    
    # First get an event ID
    list_resp = requests.get(f"{BASE_URL}/events?page=1&page_size=1")
    if list_resp.status_code != 200 or not list_resp.json().get("items"):
        print("  No events found to test")
        return None
    
    event_id = list_resp.json()["items"][0]["id"]
    url = f"{BASE_URL}/events/{event_id}"
    
    start_time = time.time()
    response = requests.get(url)
    duration = time.time() - start_time
    
    print(f"  Status: {response.status_code}")
    print(f"  Duration: {duration:.3f}s")
    
    if response.status_code == 200:
        if duration < 0.5:
            print("  ✅ Fast response - likely no N+1 queries\n")
            return True
        else:
            print("  ⚠️  Slow response - might have N+1 queries\n")
            return False
    else:
        print(f"  ❌ Request failed\n")
        return False


def run_all_tests():
    """Run all N+1 query tests."""
    print("=" * 60)
    print("N+1 QUERY TESTS")
    print("=" * 60)
    print("\nNote: Tests measure response time. < 1s is good.")
    print("Times may vary based on data size and server load.\n")
    
    results = []
    
    try:
        result = test_events_list()
        if result is not None:
            results.append(("Events List", result))
    except Exception as e:
        print(f"❌ Events list test failed: {e}\n")
        results.append(("Events List", False))
    
    try:
        result = test_event_detail()
        if result is not None:
            results.append(("Event Detail", result))
    except Exception as e:
        print(f"❌ Event detail test failed: {e}\n")
        results.append(("Event Detail", False))
    
    try:
        result = test_venues_list()
        if result is not None:
            results.append(("Venues List", result))
    except Exception as e:
        print(f"❌ Venues list test failed: {e}\n")
        results.append(("Venues List", False))
    
    try:
        result = test_tickets_endpoint()
        if result is not None:
            results.append(("User Tickets", result))
    except Exception as e:
        print(f"❌ Tickets endpoint test failed: {e}\n")
        results.append(("User Tickets", False))
    
    try:
        result = test_orders_endpoint()
        if result is not None:
            results.append(("User Orders", result))
    except Exception as e:
        print(f"❌ Orders endpoint test failed: {e}\n")
        results.append(("User Orders", False))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")


if __name__ == "__main__":
    run_all_tests()
