# Distributed LLM GPU Cluster System

## Overview

This project implements a distributed AI inference architecture for handling concurrent Large Language Model (LLM) requests using multiple GPU worker nodes.

The system combines:

* Distributed worker nodes
* Dynamic load balancing
* Retrieval-Augmented Generation (RAG)
* Fault tolerance and request reassignment
* Docker-based deployment
* GPU-accelerated inference
* Concurrent request handling
* Performance monitoring

The final architecture uses:

* One Master Node
* Multiple Worker Nodes
* Remote GPU workers hosted on Thunder Compute
* HuggingFace Transformers for inference
* FastAPI for communication

---

# System Architecture

```text
Client Requests
       │
       ▼
Master Node (Load Balancer)
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Worker Worker Worker
  1      2      3
       │
       ▼
RAG Retrieval
       │
       ▼
LLM Inference
       │
       ▼
Generated Response
```

---

# Features

## Load Balancing

* Least-loaded worker routing
* Dynamic worker selection
* Request distribution across GPU workers
* Worker load tracking

## Distributed GPU Workers

* Multiple independent worker nodes
* GPU-backed inference
* Parallel request handling
* Dockerized architecture

## RAG Integration

* Context retrieval before inference
* Lightweight retrieval system
* Query-aware contextual generation

## LLM Inference

* HuggingFace Transformers pipeline
* DistilGPT2 model
* GPU acceleration with CUDA
* Lazy model loading

## Fault Tolerance

* Worker failure detection
* Automatic retry mechanism
* Request reassignment
* System availability under worker failure

## Performance Metrics

* Latency
* Throughput
* GPU utilization

---

# Technologies Used

| Technology      | Purpose                     |
| --------------- | --------------------------- |
| Python          | Main programming language   |
| FastAPI         | REST API services           |
| Docker Compose  | Container orchestration     |
| Transformers    | LLM inference               |
| PyTorch         | GPU backend                 |
| Thunder Compute | GPU cloud workers           |
| Requests        | Inter-service communication |
| Threading       | Concurrency handling        |

---

# Project Structure

```text
Project/
│
├── common/
│   └── logger.py
│
├── llm/
│   └── inference.py
│
├── rag/
│   └── retriever.py
│
├── workers/
│   └── worker_service.py
│
├── docker_build/
│   ├── master.Dockerfile
│   ├── worker.Dockerfile
│   ├── master_requirements.txt
│   └── worker_requirements.txt
│
├── tests/
│   ├── test_health.py
│   ├── test_single_request.py
│   ├── concurrent_10.py
│   ├── concurrent_15.py
│   ├── concurrent_custom.py
│   └── test_fault_tolerance.py
│
├── config.py
├── docker-compose.yml
├── master_service.py
└── README.md
```

---

# Running the System

## Local Docker Deployment

### Start containers

```powershell
cd "D:\Me\Carol\College\Semester 6\Distributed Computing\Project"
docker compose up
```

### Health check

```powershell
Invoke-RestMethod http://localhost:7000/health
```

### Single request test

```powershell
Invoke-RestMethod `
  -Uri http://localhost:7000/submit `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"Explain load balancing"}' `
  -TimeoutSec 300
```

---

# Thunder Compute GPU Deployment

## GPU Worker Setup

### Connect to Thunder GPU instance

Use VS Code Remote SSH or Thunder extension.

### Verify GPU

```bash
nvidia-smi
```

### Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install CUDA-enabled PyTorch

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Verify CUDA

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Install dependencies

```bash
pip install fastapi uvicorn requests transformers numpy
```

### Start worker service

```bash
uvicorn workers.worker_service:app --host 0.0.0.0 --port 8000
```

---

# Connecting Master to Remote GPU Workers

Run locally:

```powershell
$env:WORKERS="https://WORKER1/process,https://WORKER2/process,https://WORKER3/process"

uvicorn master_service:app --host 0.0.0.0 --port 7000
```

---

# Testing

## Health Endpoint

```powershell
python tests/test_health.py
```

## Single Request

```powershell
python tests/test_single_request.py
```

## Concurrent Requests

```powershell
python tests/concurrent_10.py
python tests/concurrent_15.py
```

## Custom Concurrent Requests

```powershell
python tests/concurrent_custom.py 100 --retries 3
```

## 1000 Concurrent Users

```powershell
python tests/concurrent_custom.py 1000 --retries 5
```

## Fault Tolerance Test

```powershell
python tests/test_fault_tolerance.py
```

---

# Performance Metrics

The system measures:

* Request latency
* Throughput (requests/sec)
* GPU utilization

Example:

```text
Latency          : 0.358s
Throughput       : 0.047
GPU utilization  : 50.0%
```

---

# Fault Tolerance

The system automatically:

* detects failed workers
* retries requests
* reassigns tasks to active workers

Example:

```text
Thunder GPU Worker 2 failed
```

while requests continue successfully.

---

# Scalability

The architecture supports horizontal scaling by:

* adding more worker nodes
* adding more GPU instances
* increasing concurrent request handling

Final testing successfully simulated:

```text
1000 concurrent users
1000 successful requests
```

using multiple Thunder GPU workers.

---

# Limitations

* Lightweight DistilGPT2 model used for local efficiency
* GPU utilization partially simulated
* Local Docker deployment limited by laptop hardware
* Real production systems would require:

  * larger GPU clusters
  * distributed queues
  * orchestration systems such as Kubernetes

---

# Future Improvements

* Larger LLM models
* Kubernetes deployment
* Asynchronous batching
* Distributed queue system
* Vector databases
* Autoscaling GPU workers
* Real GPU monitoring dashboards

---

# Authors

* [Student Name]
* [Student Name]
* [Student Name]
