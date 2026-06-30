import requests

api_key = "sk-kimi-VmUhOTMJmtewEgBe7OZzPrCgImy4FpMSZWn8hsi2vaZnFSwOlzqwTy9EBscZVJbo"

# Test Kimi coding-specific endpoints
endpoints = [
    "https://api.kimi.com/coding/v1/models",
    "https://api.kimi.com/coding/models",
]

for url in endpoints:
    print(f"Testing endpoint: {url}")
    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error testing {url}: {e}")
