import urllib.request

try:
    req = urllib.request.Request("http://localhost:8000/api/v1/admin/users?role=user")
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError Status:", e.code)
    print("Error Body:", e.read().decode())
except Exception as e:
    print("Exception:", e)
