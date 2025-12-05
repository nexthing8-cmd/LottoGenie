#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.

# Define port
PORT=${PORT:-8000}

# Run Gunicorn with Uvicorn workers
# -w 4: 4 worker processes
# -k uvicorn.workers.UvicornWorker: Use Uvicorn for handling requests
# --bind 0.0.0.0:$PORT: Bind to all interfaces on the specified port
exec gunicorn src.web_app:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile -
