import requests
import concurrent.futures
import time

URL = "http://localhost:7000/submit"

queries = [
    "Explain load balancing",
    "What is RAG?",
    "Explain scalability",
    "What is fault tolerance?",
    "How does distributed computing work?"
]


def send_request(request_id):
    query = queries[request_id % len(queries)]

    try:
        start = time.perf_counter()

        response = requests.post(
            URL,
            json={"query": query},
            timeout=300
        )

        elapsed = time.perf_counter() - start

        if response.status_code == 200:
            data = response.json()

            print("\n==============================")
            print(f"Request #{request_id + 1}")
            print(f"Worker: {data['selected_worker']}")
            print(f"Latency: {data['performance_metrics']['Latency']}")
            print(f"Throughput: {data['performance_metrics']['Throughput']}")
            print(f"GPU Utilization: {data['performance_metrics']['GPU utilization']}")
            print("==============================")

        else:
            print(f"Request {request_id + 1} failed")

    except Exception as e:
        print(f"Request {request_id + 1} error: {e}")


print("\n====================================")
print(" RUNNING 15 CONCURRENT REQUESTS")
print("====================================")

start_total = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    executor.map(send_request, range(15))

total_time = time.perf_counter() - start_total

print("\n====================================")
print(" TEST FINISHED")
print("====================================")
print(f"Total Time: {total_time:.2f}s")