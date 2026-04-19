"""Test rate limiting functionality."""
import time
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000/api/v1"


def test_login_rate_limit():
    """Test that login endpoint is rate limited."""
    print("Testing login rate limiting (10/minute)...")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    responses = []
    # Send 15 requests quickly
    for i in range(15):
        response = requests.post(url, json=payload)
        responses.append((i+1, response.status_code))
        print(f"  Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"  ✅ Rate limit triggered at request {i+1}")
            break
    
    # Check if we got rate limited
    status_codes = [r[1] for r in responses]
    if 429 in status_codes:
        print("✅ Login rate limiting is working\n")
        return True
    else:
        print("❌ Rate limiting not triggered\n")
        return False


def test_register_rate_limit():
    """Test that register endpoint is rate limited."""
    print("Testing register rate limiting (5/minute)...")
    
    url = f"{BASE_URL}/auth/register"
    
    responses = []
    # Send 8 requests quickly
    for i in range(8):
        payload = {
            "email": f"test{i}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        response = requests.post(url, json=payload)
        responses.append((i+1, response.status_code))
        print(f"  Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"  ✅ Rate limit triggered at request {i+1}")
            break
    
    # Check if we got rate limited
    status_codes = [r[1] for r in responses]
    if 429 in status_codes:
        print("✅ Register rate limiting is working\n")
        return True
    else:
        print("❌ Rate limiting not triggered\n")
        return False


def test_otp_rate_limit():
    """Test that OTP endpoints are rate limited."""
    print("Testing OTP rate limiting (3/minute)...")
    
    url = f"{BASE_URL}/otp/email/send"
    payload = {"email": "test@example.com"}
    
    responses = []
    # Send 6 requests quickly
    for i in range(6):
        response = requests.post(url, json=payload)
        responses.append((i+1, response.status_code))
        print(f"  Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"  ✅ Rate limit triggered at request {i+1}")
            break
    
    # Check if we got rate limited
    status_codes = [r[1] for r in responses]
    if 429 in status_codes:
        print("✅ OTP rate limiting is working\n")
        return True
    else:
        print("❌ Rate limiting not triggered\n")
        return False


def test_concurrent_requests():
    """Test rate limiting under concurrent load."""
    print("Testing rate limiting with concurrent requests...")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    def make_request(i):
        response = requests.post(url, json=payload)
        return (i, response.status_code)
    
    # Send 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    results.sort()
    
    success_count = sum(1 for _, status in results if status == 401)  # Wrong password
    rate_limited_count = sum(1 for _, status in results if status == 429)
    
    print(f"  Successful requests: {success_count}")
    print(f"  Rate limited requests: {rate_limited_count}")
    
    if rate_limited_count > 0:
        print("✅ Concurrent rate limiting is working\n")
        return True
    else:
        print("❌ No rate limiting under concurrent load\n")
        return False


def run_all_tests():
    """Run all rate limiting tests."""
    print("=" * 60)
    print("RATE LIMITING TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    try:
        results.append(("Login Rate Limit", test_login_rate_limit()))
    except Exception as e:
        print(f"❌ Login rate limit test failed: {e}\n")
        results.append(("Login Rate Limit", False))
    
    # Wait a bit between tests
    time.sleep(2)
    
    try:
        results.append(("Register Rate Limit", test_register_rate_limit()))
    except Exception as e:
        print(f"❌ Register rate limit test failed: {e}\n")
        results.append(("Register Rate Limit", False))
    
    time.sleep(2)
    
    try:
        results.append(("OTP Rate Limit", test_otp_rate_limit()))
    except Exception as e:
        print(f"❌ OTP rate limit test failed: {e}\n")
        results.append(("OTP Rate Limit", False))
    
    time.sleep(2)
    
    try:
        results.append(("Concurrent Requests", test_concurrent_requests()))
    except Exception as e:
        print(f"❌ Concurrent requests test failed: {e}\n")
        results.append(("Concurrent Requests", False))
    
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
