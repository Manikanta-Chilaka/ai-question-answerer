import requests

response = requests.post(
    "http://127.0.0.1:8000/ask",
    json={"question": "a" * 2001}
)
print("status: ", response.status_code)
print("Response: ", response.json())