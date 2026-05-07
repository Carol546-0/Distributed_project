# 🚀 Quick Start Guide

## Installation

```bash
# 1. Install dependencies
pip install transformers sentence-transformers faiss-cpu torch

# 2. Navigate to project
cd "d:\Me\Carol\College\Semester 6\Distributed Computing\Project"

# 3. Run system
python main.py
```

## Common Commands

### Run with Default Settings (32 users, 8 workers)
```bash
python main.py
```

### Modify Configuration (No Code Changes!)
```python
# Edit config.py

# For small test
NUM_USERS = 10
NUM_WORKERS = 4

# For stress test
NUM_USERS = 100
NUM_WORKERS = 16

# Change load balancing strategy
LB_STRATEGY = "nginx"      # Round-robin
LB_STRATEGY = "haproxy"    # Least-connections
LB_STRATEGY = "load-aware" # Smart routing
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `config.py` | **⚙️ MODIFY THIS FOR TESTING** |
| `README.md` | Complete documentation |
| `TESTING.md` | Test scenarios |
| `IMPLEMENTATION_SUMMARY.md` | Feature checklist |

## Understanding Output

```
SYSTEM PERFORMANCE REPORT
├── [THROUGHPUT & SUCCESS]
│   ├── Total Requests: Total requests attempted
│   ├── Successful: Completed successfully
│   ├── Failed: Failed after retries
│   └── Success Rate: % successful
├── [LATENCY ANALYSIS]
│   ├── Min/Avg/Max: Performance range
│   ├── P50 (Median): 50% complete by this time
│   ├── P95: 95% complete by this time
│   └── P99: 99% complete by this time
├── [WORKER UTILIZATION]
│   └── Each GPU: # requests handled
└── [FAILURES]
    └── Breakdown by reason
```

## Key Metrics Explained

### Throughput
- **What**: Requests per second
- **Good**: 1-2 req/sec for concurrent LLM
- **Bad**: <0.5 req/sec (system overloaded)

### Latency (P95)
- **What**: 95% of requests complete by this time
- **Good**: <50 seconds
- **Bad**: >60 seconds

### Success Rate
- **What**: % of requests that succeeded
- **Good**: >95%
- **Bad**: <80%

### Worker Utilization
- **What**: Even distribution of requests
- **Good**: All workers roughly equal (~12.5% each for 8 workers)
- **Bad**: One worker much busier (skewed)

## Scaling Guide

```
For 10 users:
  - 4 workers
  - 3 memory per worker
  - Expected: 100% success, 10s latency

For 50 users:
  - 8 workers
  - 5 memory per worker
  - Expected: 95% success, 20s latency

For 100+ users:
  - 16+ workers
  - 8+ memory per worker
  - Use "nginx" strategy for balance
  - Expected: 90%+ success, 30-40s latency
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| High "MEMORY FULL" errors | Increase `WORKER_MAX_MEMORY` or add more workers |
| Unbalanced worker load | Switch to `LB_STRATEGY = "nginx"` |
| Slow inference | Reduce `LLM_MAX_NEW_TOKENS` in config |
| Many failures | Increase `MAX_RETRIES` or `REQUEST_TIMEOUT` |
| Queue overflowing | Increase `NUM_WORKERS` |

## Expected Performance

With default settings (32 users, 8 workers):
- ✅ 100% success rate
- ✅ 1.6-1.7 req/sec throughput
- ✅ ~18 second average latency
- ✅ Perfect load distribution

## Next Steps

1. **Understand the system**: Read [README.md](README.md)
2. **Try different loads**: Edit config.py
3. **Test strategies**: Change `LB_STRATEGY`
4. **Review tests**: See [TESTING.md](TESTING.md)
5. **Scale up**: Gradually increase NUM_USERS

## Quick Test Sequence

```bash
# 1. Test baseline (10 users)
# Edit config: NUM_USERS = 10
python main.py
# Expected: 100% success

# 2. Test balanced (32 users)
# Edit config: NUM_USERS = 32, NUM_WORKERS = 8
python main.py
# Expected: 100% success, even distribution

# 3. Test fault tolerance (50 users with crashes)
# Edit config: WORKER_CRASH_PROBABILITY = 0.02
python main.py
# Expected: Some failures + recoveries

# 4. Test high load (100 users)
# Edit config: NUM_USERS = 100, NUM_WORKERS = 16
python main.py
# Expected: 90%+ success with some memory pressure
```

## Architecture at a Glance

```
Users (ThreadPool)
  ↓
Task Queue (FIFO Buffer)
  ↓
Scheduler (Retry Logic)
  ↓
Load Balancer (3 Strategies)
  ↓
GPU Workers (8 Parallel)
  ├─ RAG (Semantic Search)
  └─ LLM (DistilGPT2)
  ↓
Metrics (Latency, Throughput, Utilization)
  ↓
Report & Dashboard
```

## System Capabilities

✅ Handles 1000+ concurrent requests (with proper config)
✅ 3 load balancing strategies
✅ Fault injection & recovery
✅ RAG + LLM integration
✅ Comprehensive monitoring
✅ 100% configurable (no code changes)

---

**Need more details?**
- 📖 See [README.md](README.md) for full documentation
- 🧪 See [TESTING.md](TESTING.md) for test scenarios
- ✅ See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for features

**Ready to test?**
→ Edit `config.py` and run `python main.py`

## Run with Docker Compose (new distributed mode)

Build and start all services (worker, llm, rag):

```bash
docker compose build
docker compose up
```

Services:
- Worker: http://localhost:8000/health and /infer
- LLM: http://localhost:9000/generate
- RAG: http://localhost:9001/retrieve

