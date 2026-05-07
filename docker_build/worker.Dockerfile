FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal system deps to keep image small and avoid compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only the worker-related files to keep the build context small
COPY docker_build/worker_requirements.txt /app/worker_requirements.txt
COPY workers /app/workers
COPY rag /app/rag
COPY llm /app/llm
COPY common /app/common
COPY config.py /app/config.py

# Install Python packages using binary wheels only (no compiling).
# Use PyTorch CPU wheel index to fetch the CPU-only torch wheel.
RUN pip install --no-cache-dir --only-binary=:all: -r /app/worker_requirements.txt \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

EXPOSE 8000

CMD ["uvicorn", "workers.worker_service:app", "--host", "0.0.0.0", "--port", "8000"]
