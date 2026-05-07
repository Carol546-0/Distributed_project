import requests
import concurrent.futures
import time

URL = "http://localhost:7000/submit"

queries = [
    "Explain load balancing",
    "What is RAG?",
    "Explain scalability",
    "What is distributed computing",
    "Explain GPU utilization"
]

def send_request(query):
    try:
        response = requests.post(
            URL,
            json={"query": query},
            timeout=240
        )

        return response.json()

    except Exception as e:
        return {"error": str(e)}

start = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(send_request, q) for q in queries]

    results = [f.result() for f in futures]

elapsed = time.perf_counter() - start

print("\n===== RESULTS =====")

for r in results:
    print(r)
    print()

print(f"Total Execution Time: {elapsed:.2f}s")