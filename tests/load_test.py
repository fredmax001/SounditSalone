"""Simple load testing script."""
import time
import requests
import concurrent.futures
import statistics

BASE_URL = "http://localhost:8000/api/v1"


def load_test_endpoint(name, url, method="GET", payload=None, headers=None, num_requests=100, concurrent=10):
    """Load test an endpoint."""
    print(f"\n{'=' * 60}")
    print(f"Load Testing: {name}")
    print(f"{'=' * 60}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Total Requests: {num_requests}")
    print(f"Concurrent: {concurrent}")
    
    results = []
    errors = []
    
    def make_request(i):
        try:
            start = time.time()
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=30)
            else:
                resp = requests.post(url, json=payload, headers=headers, timeout=30)
            duration = time.time() - start
            return (i, resp.status_code, duration, None)
        except Exception as e:
            return (i, None, None, str(e))
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            idx, status, duration, error = future.result()
            if error:
                errors.append(error)
            else:
                results.append((idx, status, duration))
    
    total_time = time.time() - start_time
    
    # Calculate stats
    if results:
        durations = [r[2] for r in results]
        status_codes = [r[1] for r in results]
        
        success_count = sum(1 for s in status_codes if 200 <= s < 300)
        error_count = len([s for s in status_codes if s >= 400])
        
        print(f"\nResults:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Successful: {success_count}/{num_requests}")
        print(f"  Errors (4xx/5xx): {error_count}")
        print(f"  Connection Errors: {len(errors)}")
        print(f"  Requests/sec: {num_requests/total_time:.2f}")
        print(f"\nResponse Times:")
        print(f"  Min: {min(durations)*1000:.2f}ms")
        print(f"  Max: {max(durations)*1000:.2f}ms")
        print(f"  Mean: {statistics.mean(durations)*1000:.2f}ms")
        print(f"  Median: {statistics.median(durations)*1000:.2f}ms")
        
        if len(durations) > 1:
            print(f"  Std Dev: {statistics.stdev(durations)*1000:.2f}ms")
        
        # Percentiles
        sorted_durations = sorted(durations)
        p95_idx = int(len(sorted_durations) * 0.95)
        p99_idx = int(len(sorted_durations) * 0.99)
        print(f"  P95: {sorted_durations[p95_idx]*1000:.2f}ms")
        print(f"  P99: {sorted_durations[p99_idx]*1000:.2f}ms")
        
        # Status code distribution
        status_dist = {}
        for s in status_codes:
            status_dist[s] = status_dist.get(s, 0) + 1
        print(f"\nStatus Codes:")
        for code, count in sorted(status_dist.items()):
            print(f"  {code}: {count}")
        
        return {
            "name": name,
            "total_requests": num_requests,
            "successful": success_count,
            "failed": error_count,
            "rps": num_requests/total_time,
            "mean_ms": statistics.mean(durations)*1000,
            "p95_ms": sorted_durations[p95_idx]*1000,
        }
    else:
        print(f"\n❌ All requests failed!")
        for e in errors[:5]:
            print(f"  Error: {e}")
        return None


def main():
    """Run load tests on key endpoints."""
    print("=" * 60)
    print("LOAD TESTING SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health check (lightweight)
    result = load_test_endpoint(
        "Health Check",
        f"{BASE_URL}/health",
        num_requests=200,
        concurrent=20
    )
    if result:
        results.append(result)
    
    time.sleep(2)
    
    # Test 2: Events list (read-heavy)
    result = load_test_endpoint(
        "Events List",
        f"{BASE_URL}/events?page=1&page_size=20",
        num_requests=100,
        concurrent=10
    )
    if result:
        results.append(result)
    
    time.sleep(2)
    
    # Test 3: Venues list
    result = load_test_endpoint(
        "Venues List",
        f"{BASE_URL}/venues?page=1&page_size=20",
        num_requests=100,
        concurrent=10
    )
    if result:
        results.append(result)
    
    time.sleep(2)
    
    # Test 4: Search endpoint
    result = load_test_endpoint(
        "Search Events",
        f"{BASE_URL}/events/search?query=music",
        num_requests=50,
        concurrent=5
    )
    if result:
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("LOAD TEST SUMMARY")
    print("=" * 60)
    
    if results:
        print(f"\n{'Endpoint':<20} {'RPS':>10} {'Mean (ms)':>12} {'P95 (ms)':>12}")
        print("-" * 60)
        for r in results:
            print(f"{r['name']:<20} {r['rps']:>10.2f} {r['mean_ms']:>12.2f} {r['p95_ms']:>12.2f}")
        
        avg_rps = statistics.mean([r['rps'] for r in results])
        print(f"\nAverage RPS: {avg_rps:.2f}")
    else:
        print("\nNo successful tests completed.")


if __name__ == "__main__":
    main()
