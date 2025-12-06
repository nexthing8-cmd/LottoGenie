FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (some libraries might need build tools)
# For now, sqlite is built-in.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command (can be overridden by docker-compose)
CMD ["python", "main.py", "web"]
