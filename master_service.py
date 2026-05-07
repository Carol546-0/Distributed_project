from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import time
import random
import threading

app = FastAPI()

WORKERS = os.environ.get(
    "WORKERS",
    "http://worker_node_1:8000/process,http://worker_node_2:8000/process,http://worker_node_3:8000/process",
).split(",")

worker_load = {worker: 0 for worker in WORKERS}

request_count = 0
start_time_global = time.perf_counter()
metrics_lock = threading.Lock()


class TaskRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    elapsed = time.perf_counter() - start_time_global

    with metrics_lock:
        throughput = request_count / elapsed if elapsed > 0 else 0

        return {
            "status": "master running",
            "available_workers": len(WORKERS),
            "workers": WORKERS,
            "current_worker_load": dict(worker_load),
            "completed_requests": request_count,
            "uptime_seconds": round(elapsed, 3),
            "throughput_requests_per_second": round(throughput, 3)
        }


@app.get("/metrics")
def metrics():
    elapsed = time.perf_counter() - start_time_global

    with metrics_lock:
        throughput = request_count / elapsed if elapsed > 0 else 0

        return {
            "performance_metrics": {
                "completed_requests": request_count,
                "uptime_seconds": round(elapsed, 3),
                "throughput_requests_per_second": round(throughput, 3),
                "worker_load": dict(worker_load)
            }
        }


def get_least_loaded_worker(exclude=None):
    exclude = exclude or set()

    available = {
        worker: load
        for worker, load in worker_load.items()
        if worker not in exclude
    }

    if not available:
        return None

    min_load = min(available.values())
    candidates = [w for w, load in available.items() if load == min_load]

    return random.choice(candidates)


@app.post("/submit")
def submit(task: TaskRequest):
    global request_count

    start = time.perf_counter()
    errors = []
    tried_workers = set()

    for _ in range(len(WORKERS)):
        worker_url = get_least_loaded_worker(exclude=tried_workers)

        if worker_url is None:
            break

        tried_workers.add(worker_url)

        with metrics_lock:
            worker_load[worker_url] += 1

        try:
            print(f"[MASTER] Trying worker: {worker_url}", flush=True)

            response = requests.post(
                worker_url,
                json={"query": task.query},
                timeout=180
            )
            response.raise_for_status()

            worker_response = response.json()

            latency = time.perf_counter() - start

            with metrics_lock:
                request_count += 1
                elapsed = time.perf_counter() - start_time_global
                throughput = request_count / elapsed if elapsed > 0 else 0
                current_load_snapshot = dict(worker_load)

            print(f"[MASTER] Success from worker: {worker_url}", flush=True)

            worker_id = worker_url.split("worker_node_")[-1].split(":")[0]

            if errors:
                fault_msg = " / ".join(
                f"Worker {e['worker'].split('worker_node_')[-1].split(':')[0]} failed"
                for e in errors
            )
            else:
                fault_msg = "No failed attempts"

            return {
                "status": "success",
                "selected_worker": worker_id,
                "fault_tolerance": fault_msg,
                "performance_metrics": {
                    "Latency": f"{round(latency, 3)}s",
                    "Throughput": round(throughput, 3),
                    "GPU utilization": f"{worker_response.get('gpu_utilization_end', 0)}%"
                },
                "worker_result": {
                    "query": worker_response.get("query", task.query),
                    "context": worker_response.get("context", ""),
                    "answer": worker_response.get("answer", "")
                }
            }

        except Exception as e:
            print(f"[MASTER ERROR] Worker failed {worker_url}: {e}", flush=True)
            errors.append({
                "worker": worker_url,
                "error": str(e)
            })

        finally:
            with metrics_lock:
                worker_load[worker_url] = max(0, worker_load[worker_url] - 1)

    raise HTTPException(
        status_code=500,
        detail={
            "message": "All workers failed",
            "tried_workers": list(tried_workers),
            "errors": errors
        }
    )