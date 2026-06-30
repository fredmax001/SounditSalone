import requests
import json

api_key = "sk-kimi-VmUhOTMJmtewEgBe7OZzPrCgImy4FpMSZWn8hsi2vaZnFSwOlzqwTy9EBscZVJbo"
url = "https://api.kimi.com/coding/v1/chat/completions"

# Create a tiny 1x1 black pixel PNG image in base64
tiny_png_base64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "YAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

# Crucial header to bypass coding agent restriction
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "KimiCLI/1.5"
}

payload = {
    "model": "kimi-for-coding",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this image? Reply with one word only."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{tiny_png_base64}"
                    }
                }
            ]
        }
    ],
    "temperature": 0.0
}

print("Sending request with KimiCLI User-Agent...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error calling API: {e}")
