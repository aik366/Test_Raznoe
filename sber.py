import requests

response = requests.post(
    "https://api.finam.ru/v1/sessions",
    headers={
        "Content-Type": "application/json"
    },
    json={
    "secret": "your-api-secret-key"
}
)
data = response.json()
print(data)