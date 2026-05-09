import requests
import concurrent.futures
import time
import argparse
from collections import Counter

URL = "http://localhost:7000/submit"

queries = [
    "Explain load balancing",
    "What is RAG?",
    "Explain scalability",
    "What is fault tolerance?",
    "Explain GPU utilization?"
]


def send_request(request_id, retries):
    query = queries[request_id % len(queries)]

    for attempt in range(1, retries + 2):
        try:
            start = time.perf_counter()

            response = requests.post(
                URL,
                json={"query": query},
                timeout=600
            )

            elapsed = time.perf_counter() - start

            if response.status_code == 200:
                data = response.json()
                metrics = data["performance_metrics"]

                return {
                    "id": request_id + 1,
                    "status": "success",
                    "worker": data["selected_worker"],
                    "latency": metrics["Latency"],
                    "throughput": metrics["Throughput"],
                    "gpu": metrics["GPU utilization"],
                    "fault_tolerance": data.get("fault_tolerance", "No failed attempts"),
                    "attempts": attempt,
                    "elapsed": elapsed
                }

        except Exception:
            time.sleep(0.5)

    return {
        "id": request_id + 1,
        "status": "error",
        "worker": "-",
        "latency": "-",
        "throughput": "-",
        "gpu": "-",
        "attempts": retries + 1,
        "fault_tolerance": "Request failed"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("users", type=int, help="Number of concurrent users/requests")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries per failed request")
    args = parser.parse_args()

    total_requests = args.users
    max_threads = total_requests

    print("\n====================================")
    print(f" RUNNING {total_requests} CONCURRENT USERS")
    print("====================================")
    print(f"Retries per request: {args.retries}")

    start_total = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(send_request, i, args.retries)
            for i in range(total_requests)
        ]

        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    total_time = time.perf_counter() - start_total

    results.sort(key=lambda x: x["id"])

    print("\nRequest Results:")
    print("-" * 110)
    print(f"{'Req':<6}{'Status':<12}{'Worker':<24}{'Latency':<12}{'Throughput':<14}{'GPU Util':<12}{'Attempts':<10}{'Fault Tolerance'}")
    print("-" * 110)

    for r in results:
        print(
            f"{r['id']:<6}"
            f"{r['status']:<12}"
            f"{r['worker']:<24}"
            f"{r['latency']:<12}"
            f"{r['throughput']:<14}"
            f"{r['gpu']:<12}"
            f"{r['attempts']:<10}"
            f"{r['fault_tolerance']}"
        )

    print("-" * 110)

    successful = [r for r in results if r["status"] == "success"]
    failed = len(results) - len(successful)
    worker_counts = Counter(r["worker"] for r in successful)

    throughput = len(successful) / total_time if total_time > 0 else 0

    print("\nSummary:")
    print(f"Total Concurrent Users : {total_requests}")
    print(f"Successful             : {len(successful)}")
    print(f"Failed                 : {failed}")
    print(f"Total Test Time        : {total_time:.2f}s")
    print(f"Overall Throughput     : {throughput:.2f} req/s")
    print(f"Worker Distribution    : {dict(worker_counts)}")
    print("====================================\n")


if __name__ == "__main__":
    main()