# 🧪 Test Scenarios & Benchmarking

This file documents test scenarios for validating the distributed LLM system.

---

## Test Scenario 1: Baseline (Small Load)

**Configuration:**
```python
NUM_USERS = 10
NUM_WORKERS = 4
WORKER_MAX_MEMORY = 3
LB_STRATEGY = "haproxy"
WORKER_CRASH_PROBABILITY = 0.0
```

**Expected Results:**
- ✅ 100% success rate
- ✅ Throughput: ~1.0 req/sec
- ✅ Avg Latency: ~10 sec
- ✅ Balanced worker distribution

**Run:**
```bash
# Edit config.py with above values
python main.py
```

---

## Test Scenario 2: Balanced Load Distribution

**Configuration:**
```python
NUM_USERS = 32
NUM_WORKERS = 8
WORKER_MAX_MEMORY = 5
LB_STRATEGY = "nginx"  # Round-robin for balanced distribution
WORKER_CRASH_PROBABILITY = 0.0
```

**Expected Results:**
- ✅ 100% success rate
- ✅ Throughput: ~1.6-1.7 req/sec
- ✅ Avg Latency: ~18-19 sec
- ✅ Perfect worker distribution (4 req per worker)
- ✅ Each worker gets exactly 12.5% of traffic

**Run:**
```bash
python main.py
```

**Key Metric:**
```
Worker Utilization Snapshot:
GPU 0: #--------- 0.12 (4 reqs)
GPU 1: #--------- 0.12 (4 reqs)
GPU 2: #--------- 0.12 (4 reqs)
...
```

---

## Test Scenario 3: Fault Tolerance Test

**Configuration:**
```python
NUM_USERS = 50
NUM_WORKERS = 8
WORKER_MAX_MEMORY = 5
LB_STRATEGY = "nginx"
WORKER_CRASH_PROBABILITY = 0.02  # 2% crash rate
WORKER_RECOVERY_PROBABILITY = 0.40
MAX_RETRIES = 3
```

**Expected Results:**
- ⚠️ Some failures expected (GPU crashes)
- ✅ Retries recover most failures
- ✅ Success rate: 80-95%
- ✅ System continues despite worker failures

**Run:**
```bash
python main.py
```

**What to Observe:**
```
[GPU-X] CRASHED  # Worker failure
[Scheduler] Retrying...  # Automatic retry
[GPU-Y] Processing Req  # Reassignment to new worker
[GPU-Y] Completed Req   # Success after retry
```

**Failure Breakdown:**
```
[FAILURE BREAKDOWN]
GPU 0 MEMORY FULL: 5
GPU 3 CRASHED: 1
GPU 7 CRASHED: 2
```

---

## Test Scenario 4: Memory Pressure Test

**Configuration:**
```python
NUM_USERS = 100
NUM_WORKERS = 4  # Fewer workers → more memory pressure
WORKER_MAX_MEMORY = 3  # Limited memory
LB_STRATEGY = "haproxy"
```

**Expected Results:**
- ⚠️ Many "MEMORY FULL" failures
- ✅ System demonstrates graceful degradation
- ✅ Retries eventually succeed
- ✅ Load balancer redirects to less busy workers

**Run:**
```bash
python main.py
```

**What to Observe:**
```
Failure Breakdown:
GPU 0 MEMORY FULL: 45
GPU 1 MEMORY FULL: 32
GPU 2 MEMORY FULL: 28
GPU 3 MEMORY FULL: 35
```

---

## Test Scenario 5: High Concurrency Scale Test

**Configuration:**
```python
NUM_USERS = 200
NUM_WORKERS = 16
WORKER_MAX_MEMORY = 8
LB_STRATEGY = "nginx"
MAX_CONCURRENT_THREADS = 150
```

**Expected Results:**
- ✅ Handles 200+ concurrent requests
- ✅ Throughput: 1.5-2.0 req/sec
- ✅ System stability maintained
- ✅ Balanced worker load

**Run:**
```bash
python main.py
```

**Performance Metrics:**
```
Throughput: 1.8 req/sec
Avg Latency: ~25 sec (increased due to more concurrent work)
Success Rate: 95%+
```

---

## Test Scenario 6: Strategy Comparison

Run each load balancing strategy and compare:

### 6A: Round-Robin (NGINX)
```python
LB_STRATEGY = "nginx"
NUM_USERS = 50
```
**Expected:** Perfect even distribution

### 6B: Least-Connections (HAProxy)
```python
LB_STRATEGY = "haproxy"
NUM_USERS = 50
```
**Expected:** Smart routing based on active requests

### 6C: Load-Aware
```python
LB_STRATEGY = "load-aware"
NUM_USERS = 50
```
**Expected:** Considers both connections and memory

**Comparison Script:**
```bash
# Test NGINX
echo "Testing NGINX (Round-Robin)..."
sed -i 's/LB_STRATEGY = .*/LB_STRATEGY = "nginx"/g' config.py
python main.py > results_nginx.txt

# Test HAProxy
echo "Testing HAProxy (Least-Connections)..."
sed -i 's/LB_STRATEGY = .*/LB_STRATEGY = "haproxy"/g' config.py
python main.py > results_haproxy.txt

# Test Load-Aware
echo "Testing Load-Aware..."
sed -i 's/LB_STRATEGY = .*/LB_STRATEGY = "load-aware"/g' config.py
python main.py > results_load_aware.txt

# Compare throughput
grep "Throughput" results_*.txt
```

---

## Test Scenario 7: Extreme Stress Test

**Configuration:**
```python
NUM_USERS = 500
NUM_WORKERS = 32
WORKER_MAX_MEMORY = 10
LB_STRATEGY = "nginx"
MAX_CONCURRENT_THREADS = 200
WORKER_CRASH_PROBABILITY = 0.005  # Rare crashes
```

**Expected Results:**
- ✅ System handles 500+ concurrent users
- ✅ Throughput: 1.5-2.5 req/sec
- ✅ Latency degradation acceptable
- ✅ No deadlocks or system crashes

**Run:**
```bash
# WARNING: This will take ~5 minutes
python main.py
```

**Expected Output Summary:**
```
Total Requests     : 500
Successful         : 475
Failed             : 25
Success Rate       : 95.0%
Throughput         : 2.1 req/sec
Avg Latency        : 45 sec
P95 Latency        : 55 sec
```

---

## Test Scenario 8: Latency SLA Validation

**Configuration:**
```python
NUM_USERS = 100
NUM_WORKERS = 12
WORKER_MAX_MEMORY = 6
LB_STRATEGY = "nginx"
```

**SLA Targets:**
- P50 Latency: < 30 sec
- P95 Latency: < 50 sec
- P99 Latency: < 60 sec
- Success Rate: > 95%

**Validation Script:**
```python
# In metrics.py report()
p95 = self.p95_latency()
p99 = self.p99_latency()

sla_met = (
    p95 < 50 and 
    p99 < 60 and 
    self.success_rate() > 95
)

if sla_met:
    log("✅ SLA MET")
else:
    log("❌ SLA VIOLATED")
```

---

## Test Scenario 9: Recovery Time Measurement

**Configuration:**
```python
NUM_USERS = 50
NUM_WORKERS = 8
WORKER_CRASH_PROBABILITY = 0.05  # Higher crash rate
WORKER_RECOVERY_PROBABILITY = 0.50  # Faster recovery
```

**Metrics to Track:**
1. Time to first failure
2. Time between failure and retry
3. Time to recovery
4. Number of retries until success

**Observation Points:**
```
[Time 10s] GPU-3 CRASHED
[Time 10.2s] Scheduler detected failure
[Time 10.3s] Retry on GPU-5
[Time 20s] Request completed successfully (after 10s)
```

---

## Test Scenario 10: Queue Depth Analysis

**Configuration:**
```python
NUM_USERS = 100
NUM_WORKERS = 4  # Limited workers → queue buildup
```

**Expected Behavior:**
```
[QUEUE SIZE OVER TIME]
[1, 2, 3, 4, 5, 10, 15, 25, 40, 35, 20, 10, 5, 2, 1]
```

**Peak queue depth indicates:**
- How much buffering capacity needed
- Whether producers are faster than consumers
- If load balancer is keeping up

---

## Automated Test Runner

**Create `run_tests.py`:**

```python
import subprocess
import json
from config import *

test_configs = [
    {
        "name": "Small Load",
        "users": 10,
        "workers": 4,
        "workers_memory": 3
    },
    {
        "name": "Balanced",
        "users": 32,
        "workers": 8,
        "workers_memory": 5
    },
    {
        "name": "Fault Tolerance",
        "users": 50,
        "workers": 8,
        "workers_memory": 5,
        "crash_prob": 0.02
    },
    {
        "name": "High Concurrency",
        "users": 200,
        "workers": 16,
        "workers_memory": 8
    }
]

results = []

for test in test_configs:
    print(f"\n{'='*60}")
    print(f"Running: {test['name']}")
    print(f"{'='*60}")
    
    # Update config
    with open('config.py', 'r') as f:
        config_content = f.read()
    
    config_content = config_content.replace(
        f"NUM_USERS = {NUM_USERS}",
        f"NUM_USERS = {test['users']}"
    )
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    
    # Run test
    result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
    
    # Extract metrics
    output = result.stdout
    results.append({
        "test": test['name'],
        "output": output
    })

# Save results
with open('test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ All tests completed. Results saved to test_results.json")
```

**Run:**
```bash
python run_tests.py
```

---

## Performance Benchmark Checklist

- [ ] **Baseline**: 10 users, 100% success
- [ ] **Scaling**: Linearly increase users, track throughput
- [ ] **Fault Tolerance**: Inject failures, verify recovery
- [ ] **Load Balancing**: Compare strategies
- [ ] **Latency Percentiles**: Track P50, P95, P99
- [ ] **Worker Utilization**: Verify even distribution
- [ ] **Queue Depth**: Monitor buildup patterns
- [ ] **Success Rate**: Target > 95%
- [ ] **Memory Pressure**: Test edge cases
- [ ] **Recovery Time**: Measure MTTR

---

## Expected Performance by Load

| Users | Workers | Throughput | Avg Latency | Success % |
|-------|---------|-----------|-------------|-----------|
| 10 | 4 | 0.9 req/s | 10 s | 100% |
| 32 | 8 | 1.7 req/s | 19 s | 100% |
| 50 | 8 | 1.5 req/s | 22 s | 95% |
| 100 | 12 | 1.8 req/s | 28 s | 95% |
| 200 | 16 | 2.1 req/s | 40 s | 90% |
| 500 | 32 | 2.3 req/s | 60 s | 85% |

---

## 📊 Interpretation Guide

### Throughput vs Users
- Should stay relatively constant (1-2 req/sec)
- If decreasing: system saturating
- If increasing: parallelization working well

### Latency Increase Pattern
- **Small increase (10-20%)**: Normal
- **Large increase (>50%)**: Memory or CPU contention
- **Exponential increase**: Queue buildup → need more workers

### Success Rate
- **100%**: System healthy
- **95-99%**: Acceptable (some transient failures)
- **<90%**: System overloaded or too many faults

### Worker Utilization
- **Even distribution**: Load balancer working well
- **Skewed**: One worker much busier than others
- **All low (<20%)**: Underutilized system

