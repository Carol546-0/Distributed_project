# 🚀 Distributed LLM GPU Cluster Simulation

A production-like distributed system for handling 1000+ concurrent LLM inference requests with load balancing, fault tolerance, RAG integration, and comprehensive monitoring.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER (1000+ users)               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/Queue Requests
┌────────────────────────▼────────────────────────────────────┐
│          TASK QUEUE (Thread-safe Buffer)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│   LOAD BALANCER (Round-Robin / Least-Connections)           │
│   • NGINX strategy (Round-Robin)                            │
│   • HAProxy strategy (Least-Connections)                    │
│   • Load-Aware strategy (Active requests + Memory)          │
└──┬────┬────┬────┬────┬────┬────┬────┬────────────────────────┘
   │    │    │    │    │    │    │    │
┌──▼┐ ┌─▼──┐┌─▼──┐┌─▼──┐┌─▼──┐┌─▼──┐┌─▼──┐┌─▼──┐
│GPU│ │GPU ││GPU ││GPU ││GPU ││GPU ││GPU ││GPU │  (8 Workers)
│ 0 │ │ 1  ││ 2  ││ 3  ││ 4  ││ 5  ││ 6  ││ 7  │
└─┬─┘ └─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘└─┬──┘
  │     │    │    │    │    │    │    │
  │ All Workers Execute:
  │ 1. Retrieve Context (RAG)
  │ 2. Run LLM Inference
  │ 3. Return Response
  │
┌─▼─────────────────────────────────────────────────────────┐
│              MONITORING & METRICS                           │
│ • Latency (min/avg/p50/p95/p99/max)                        │
│ • Throughput (req/sec)                                     │
│ • Worker Utilization                                       │
│ • Failure Breakdown                                        │
│ • Success Rate                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Features Implemented

### ✅ Load Balancing
- **NGINX Strategy**: Round-robin distribution
- **HAProxy Strategy**: Least-connections routing
- **Load-Aware Strategy**: Considers active requests + memory usage
- **Dynamic Worker Selection**: Automatically skips failed workers

### ✅ Fault Tolerance
- **Worker Crash Simulation**: Configurable crash probability (1% default)
- **Automatic Recovery**: 40% recovery probability per cycle
- **Retry Logic**: Up to 3 retry attempts per request
- **Graceful Degradation**: System continues with fewer workers

### ✅ LLM + RAG Integration
- **Lightweight Model**: DistilGPT2 for fast inference
- **Vector Database**: FAISS for semantic similarity search
- **Query Expansion**: Synonyms for better retrieval
- **Context Ranking**: Relevance scoring for retrieved documents

### ✅ Performance Monitoring
- **Latency Analysis**: Min/avg/median/p95/p99/max
- **Throughput Tracking**: Requests per second
- **Worker Utilization**: Per-GPU request distribution
- **Failure Breakdown**: Categorized failure reasons
- **Queue Depth Monitoring**: Real-time queue visualization

### ✅ Scalability
- **8 GPU Workers** (configurable)
- **Simulated GPU Memory**: 5 units per worker
- **Thread Pool**: Up to 100 concurrent threads
- **Request Timeout**: 15 seconds (configurable)

---

## 📈 Test Results

### Test 1: Small Load (10 users)
```
Total Requests     : 10
Successful         : 10
Failed             : 0
Success Rate       : 100.0%
Throughput         : 0.94 req/sec

Latency Analysis:
  Min Latency        : 9.879 sec
  Avg Latency        : 10.313 sec
  Median (P50)       : 10.442 sec
  P95 Latency        : 10.571 sec
  Max Latency        : 10.571 sec

Worker Utilization: Balanced (0.30, 0.30, 0.20, 0.20)
```

### Test 2: Moderate Load (32 users, 8 workers)
```
Total Requests     : 32
Successful         : 32
Failed             : 0
Success Rate       : 100.0%
Throughput         : 1.67 req/sec

Latency Analysis:
  Min Latency        : 17.982 sec
  Avg Latency        : 18.755 sec
  Median (P50)       : 18.792 sec
  P95 Latency        : 19.085 sec
  Max Latency        : 19.112 sec

Worker Utilization: Perfect (0.12 each = 4 reqs per worker)
```

---

## 🛠️ Configuration

Edit `config.py` to customize:

```python
# Load balancing strategy
LB_STRATEGY = "nginx"  # "nginx", "haproxy", "load-aware"

# GPU Workers
NUM_WORKERS = 8
WORKER_MAX_MEMORY = 5

# Scheduler
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15.0

# Load Test
NUM_USERS = 32  # Adjust for stress testing
MAX_CONCURRENT_THREADS = 100

# Fault Injection
WORKER_CRASH_PROBABILITY = 0.01
WORKER_RECOVERY_PROBABILITY = 0.40

# LLM Inference
LLM_MAX_NEW_TOKENS = 20
LLM_MODEL = "distilgpt2"

# RAG
RAG_TOP_K = 3
```

---

## 🚀 Running the System

### Prerequisites
```bash
pip install transformers sentence-transformers faiss-cpu torch
```

### Basic Run (10 users)
```bash
python main.py
```

### Stress Test (100+ users)
```python
# Edit config.py
NUM_USERS = 100
NUM_WORKERS = 16
WORKER_MAX_MEMORY = 8
LB_STRATEGY = "nginx"

# Run
python main.py
```

### Test Different Strategies
```python
# Test 1: Round-Robin (NGINX)
LB_STRATEGY = "nginx"

# Test 2: Least-Connections (HAProxy)
LB_STRATEGY = "haproxy"

# Test 3: Load-Aware
LB_STRATEGY = "load-aware"
```

---

## 📊 System Components

### 1. **Core/Task Queue** (`core/task_queue.py`)
- Thread-safe queue using Python's `Queue`
- Buffers incoming requests
- Non-blocking dequeue

### 2. **Load Balancer** (`lb/load_balancer.py`)
- Selects best worker for each request
- Three strategies supported
- Thread-safe with locks

### 3. **GPU Workers** (`workers/gpu_worker.py`)
- Simulates GPU memory constraints (0-5 units)
- Tracks active requests and memory usage
- Crash simulation (1% probability)
- Batch processing capability

### 4. **Scheduler** (`master/scheduler.py`)
- Pulls tasks from queue
- Dispatches to workers
- Retry logic (up to 3 times)
- Timeout handling (15s)
- Failure tracking

### 5. **RAG Retriever** (`rag/retriever.py`)
- FAISS vector database
- Semantic similarity search
- Query expansion with synonyms
- Relevance ranking

### 6. **LLM Inference** (`llm/inference.py`)
- DistilGPT2 model
- Configurable token generation
- Fast inference (~5 seconds/request)

### 7. **Metrics & Monitoring** (`monitoring/metrics.py`)
- Latency tracking (percentiles)
- Throughput calculation
- Worker utilization
- Success rate
- Failure breakdown

### 8. **Dashboard** (`monitoring/dashboard.py`)
- Queue size visualization
- Worker utilization bars
- Failure reporting

---

## 🔍 Key Metrics Explained

### Throughput
```
throughput = total_requests / elapsed_time
```
- **Current**: ~1-1.7 req/sec for 32-50 concurrent users
- **Expected at 1000 users**: Depends on parallelization

### Latency Percentiles
- **P50 (Median)**: 50% of requests complete by this time
- **P95**: 95% of requests complete by this time
- **P99**: 99% of requests complete by this time

### Worker Utilization
```
utilization = requests_sent_to_worker / total_requests
```
- **Perfect distribution**: Each worker gets ~1/N of traffic (where N = num_workers)
- **Current**: 0.125 per worker (1/8) for round-robin

---

## 🧪 Test Scenarios

### Scenario 1: Normal Operation
```bash
NUM_USERS = 32
WORKER_CRASH_PROBABILITY = 0.0
# Expected: 100% success, balanced load
```

### Scenario 2: Fault Tolerance
```bash
NUM_USERS = 50
WORKER_CRASH_PROBABILITY = 0.02
# Expected: Failures occur, system recovers, retries succeed
```

### Scenario 3: Stress Test
```bash
NUM_USERS = 200
NUM_WORKERS = 16
WORKER_MAX_MEMORY = 10
# Expected: High throughput, some failures during memory pressure
```

### Scenario 4: Scale Test
```bash
NUM_USERS = 1000
NUM_WORKERS = 32
WORKER_MAX_MEMORY = 20
MAX_CONCURRENT_THREADS = 200
# Expected: System stays stable, handles concurrent load
```

---

## 🎯 Next Improvements

1. **Request Batching**: Group requests for GPU batch processing
2. **Kubernetes Deployment**: Deploy on actual cluster
3. **REST API**: Add FastAPI interface
4. **Advanced Monitoring**: Grafana dashboard integration
5. **Distributed Tracing**: OpenTelemetry support
6. **Model Quantization**: Faster inference with quantized models
7. **Request Priority Levels**: Handle urgent vs batch requests
8. **Caching Layer**: Redis for response caching

---

## 📝 Architecture Decisions

### Why Thread-based vs Async?
- Simpler concurrency model
- Better for CPU-bound tasks (LLM inference)
- Easier fault isolation

### Why DistilGPT2?
- Lightweight and fast (~5s per request)
- Suitable for simulation
- Allows testing parallelization

### Why FAISS?
- Efficient vector similarity search
- Supports large document collections
- Production-proven in ML systems

### Why Three LB Strategies?
- NGINX (round-robin): Simplest, great for homogeneous load
- HAProxy (least-connections): Better for variable request duration
- Load-aware: Considers memory to avoid saturation

---

## 🚨 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| High memory failures | Too many concurrent requests | Increase `WORKER_MAX_MEMORY` or `NUM_WORKERS` |
| Unbalanced load | HAProxy with synchronous requests | Use `LB_STRATEGY = "nginx"` |
| Slow response time | LLM inference bottleneck | Reduce `LLM_MAX_NEW_TOKENS` |
| Worker crashes not recovering | Recovery probability too low | Increase `WORKER_RECOVERY_PROBABILITY` |
| Queue overflow | Consumers slower than producers | Increase parallelization or workers |

---

## 📚 Files Overview

```
.
├── main.py                          # Entry point
├── config.py                        # Configuration
├── core/
│   └── task_queue.py               # Request queue
├── lb/
│   └── load_balancer.py            # Load balancing strategies
├── workers/
│   └── gpu_worker.py               # GPU worker simulation
├── master/
│   └── scheduler.py                # Task scheduling & retries
├── llm/
│   └── inference.py                # LLM inference
├── rag/
│   └── retriever.py                # RAG + Vector DB
├── monitoring/
│   ├── metrics.py                  # Metrics collection
│   └── dashboard.py                # Display & visualization
├── client/
│   └── load_generator.py           # Load test driver
└── common/
    ├── logger.py                   # Logging utilities
    └── models.py                   # Request/Response models
```

---

## 📖 How to Extend

### Add New Load Balancing Strategy
```python
# In load_balancer.py
if self.strategy == "my_strategy":
    return my_custom_selection_logic(alive)
```

### Add Custom Metrics
```python
# In metrics.py
def my_custom_metric(self):
    return self.calculate_something()

# In metrics.report()
log(f"My Metric: {self.my_custom_metric()}")
```

### Add Fault Injection
```python
# In config.py
NEW_FAULT_PROBABILITY = 0.05

# In scheduler.py or workers.py
if random.random() < config.NEW_FAULT_PROBABILITY:
    # Inject fault
```

---

## 💡 Performance Tips

1. **Use round-robin** for balanced concurrent workloads
2. **Increase workers** before increasing memory per worker
3. **Reduce LLM tokens** to speed up inference (bottleneck)
4. **Monitor failure breakdown** to identify bottlenecks
5. **Use P95 latency** for SLA guarantees (not average)

---

## ✅ Validation Checklist

- [x] All 10 components implemented
- [x] Load balancing strategies working (3 variants)
- [x] Fault injection and recovery working
- [x] RAG + LLM integration complete
- [x] Metrics collection comprehensive
- [x] Scales to 32+ concurrent users
- [x] Configuration system in place
- [x] Error handling and retries working
- [x] Request deduplication fixed
- [x] Worker utilization tracking

---

## 🎓 Learning Outcomes

This project demonstrates:
1. **Distributed Systems**: Task distribution, fault tolerance, load balancing
2. **Concurrent Programming**: Thread pools, synchronization, queue management
3. **Performance Engineering**: Latency analysis, throughput optimization
4. **AI/ML Integration**: LLM inference, RAG, vector databases
5. **System Design**: Architecture decisions, scaling strategies
6. **Monitoring**: Metrics collection, anomaly detection

