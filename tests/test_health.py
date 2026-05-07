import requests

urls = [
    "http://localhost:7000/health",
    "http://localhost:8000/health"
]

for url in urls:
    try:
        response = requests.get(url)

        print(f"\n{url}")
        print(response.json())

    except Exception as e:
        print(f"{url} FAILED: {e}")