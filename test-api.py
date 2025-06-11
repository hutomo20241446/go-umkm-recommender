import requests
import json

# URL endpoint API
url = "http://localhost:8000/recommend"

# Data yang akan dikirim (sesuaikan user_id dengan yang ada di database)
payload = {
    "user_id": "defccad3-af7c-466a-bcd2-7141e2b28d42",  # Ganti dengan user_id valid
}

# Headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Melakukan POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Cek status code
    if response.status_code == 200:
        print("Request berhasil!")
        print("Response:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")