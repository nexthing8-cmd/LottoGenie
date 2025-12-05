FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (needed for mysqlclient/mariadb connector sometimes, or other build tools)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port
EXPOSE 8000

# Default command to run the web server
CMD ["python", "main.py", "web"]
