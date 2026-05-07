FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY docker_build/master_requirements.txt /app/requirements.txt
COPY master_service.py /app/master_service.py

RUN pip install --no-cache-dir --prefer-binary -r /app/requirements.txt

EXPOSE 7000

CMD ["uvicorn", "master_service:app", "--host", "0.0.0.0", "--port", "7000"]
