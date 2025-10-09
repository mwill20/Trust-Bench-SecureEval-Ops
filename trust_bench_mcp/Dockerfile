FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    TRUST_BENCH_WORKDIR=/workspace

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY trust_bench_server.py .

VOLUME ["/workspace"]

CMD ["python", "trust_bench_server.py"]
