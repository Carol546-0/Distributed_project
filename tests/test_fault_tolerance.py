# tests/test_fault_tolerance.py

import requests
import concurrent.futures
import subprocess
import time

URL = "http://localhost:7000/submit"

WORKER_CONTAINER = "project-worker_node_2-1"

queries = [
    "Explain load balancing",
    "What is RAG?",
    "Explain scalability",
    "What is fault tolerance?",
    "How does distributed computing work?"
]


def stop_worker():
    print("\n[TEST] Stopping Worker Node 2...\n")

    subprocess.run(
        ["docker", "stop", WORKER_CONTAINER],
        check=False
    )

    time.sleep(3)


def start_worker():
    print("\n[TEST] Restarting Worker Node 2...\n")

    subprocess.run(
        ["docker", "start", WORKER_CONTAINER],
        check=False
    )

    time.sleep(3)


def send_request(query):
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

            print("\n===================================")
            print(f"Query: {query}")
            print(f"Status: {data['status']}")
            print(f"Selected Worker: {data['selected_worker']}")
            print(f"Fault Tolerance: {data['fault_tolerance']}")

            metrics = data["performance_metrics"]

            print("\nPerformance Metrics:")
            print(f"Latency: {metrics['Latency']}")
            print(f"Throughput: {metrics['Throughput']}")
            print(f"GPU Utilization: {metrics['GPU utilization']}")

            print("\nGenerated Answer:")
            print(data["worker_result"]["answer"])

            print(f"\nCompleted in {elapsed:.2f}s")
            print("===================================")

        else:
            print(f"\n[ERROR] Status Code: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"\n[EXCEPTION] {query}")
        print(e)


def main():
    print("\n========================================")
    print(" DISTRIBUTED SYSTEM FAULT TOLERANCE TEST")
    print("========================================")

    stop_worker()

    print("\n[TEST] Sending concurrent requests...\n")

    start_total = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []

        for query in queries:
            futures.append(executor.submit(send_request, query))

        concurrent.futures.wait(futures)

    total_time = time.perf_counter() - start_total

    print("\n========================================")
    print(" ALL REQUESTS FINISHED")
    print("========================================")
    print(f"Total Execution Time: {total_time:.2f}s")

    start_worker()

    print("\n========================================")
    print(" WORKER NODE 2 RESTORED")
    print("========================================")


if __name__ == "__main__":
    main()