import time
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag.retriever import retrieve_context
from llm.inference import run_llm
from common.logger import log

app = FastAPI()

current_tasks = 0
MAX_CAPACITY = 2
task_lock = threading.Lock()


class WorkerRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    with task_lock:
        gpu_utilization = (current_tasks / MAX_CAPACITY) * 100

    return {
        "status": "worker running",
        "active_tasks": current_tasks,
        "max_capacity": MAX_CAPACITY,
        "gpu_utilization": gpu_utilization
    }


@app.post("/process")
def process_task(req: WorkerRequest):
    global current_tasks

    start = time.perf_counter()

    with task_lock:
        current_tasks += 1
        gpu_utilization_start = (current_tasks / MAX_CAPACITY) * 100

    try:
        print(f"[WORKER] Received request: {req.query}", flush=True)

        print("[WORKER] Starting RAG retrieval...", flush=True)
        rag_start = time.perf_counter()
        context = retrieve_context(req.query)
        rag_latency = time.perf_counter() - rag_start
        print(f"[WORKER] Finished RAG in {rag_latency:.2f}s", flush=True)

        print("[WORKER] Starting LLM inference...", flush=True)
        llm_start = time.perf_counter()
        answer = run_llm(req.query, context)
        llm_latency = time.perf_counter() - llm_start
        print(f"[WORKER] Finished LLM in {llm_latency:.2f}s", flush=True)

        total_latency = time.perf_counter() - start

        with task_lock:
            gpu_utilization_end = (current_tasks / MAX_CAPACITY) * 100

        return {
            "query": req.query,
            "context": context,
            "answer": answer,
            "latency": total_latency,
            "rag_latency": rag_latency,
            "llm_latency": llm_latency,
            "active_tasks": current_tasks,
            "max_capacity": MAX_CAPACITY,
            "gpu_utilization_start": gpu_utilization_start,
            "gpu_utilization_end": gpu_utilization_end
        }

    except Exception as e:
        log(f"[Worker service] processing error: {e}")
        print(f"[WORKER ERROR] {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        with task_lock:
            current_tasks = max(0, current_tasks - 1)