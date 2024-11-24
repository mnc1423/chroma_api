FROM python:3.11.10-bookworm AS builder
RUN apt-get update --fix-missing && apt-get install -y --fix-missing \
    build-essential \
    gcc \
    g++ \
    cmake \
    autoconf && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /install

WORKDIR /app

COPY . .

FROM python:3.11.10-bookworm

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update --fix-missing && apt-get install -y curl

WORKDIR /app

COPY --from=builder /app/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]