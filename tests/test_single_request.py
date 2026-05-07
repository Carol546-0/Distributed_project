import requests
import time

print("\n========== SINGLE REQUEST TEST ==========\n")

start = time.perf_counter()

response = requests.post(
    "http://localhost:7000/submit",
    json={"query": "Explain load balancing"},
    timeout=300
)

elapsed = time.perf_counter() - start

data = response.json()

print(f"Status              : {data['status']}")
print(f"Selected Worker     : {data['selected_worker']}")
print(f"Fault Tolerance     : {data['fault_tolerance']}")

metrics = data["performance_metrics"]

print("\nPerformance Metrics")
print(f"Latency             : {metrics['Latency']}")
print(f"Throughput          : {metrics['Throughput']}")
print(f"GPU Utilization     : {metrics['GPU utilization']}")

result = data["worker_result"]

print("\nWorker Result")
print(f"Query               : {result['query']}")
print(f"Context             : {result['context']}")
print(f"Answer              : {result['answer']}")

print(f"\nTotal Test Time     : {elapsed:.2f}s")

print("\n=========================================\n")