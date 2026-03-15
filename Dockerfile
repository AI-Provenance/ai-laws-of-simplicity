# Dockerfile
# Reproducible experiment environment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy experiment code
COPY experiment/ ./experiment/
COPY scripts/ ./scripts/
COPY skills/ ./skills/

# Create data directories
RUN mkdir -p data/raw data/results

# Set entry point
ENTRYPOINT ["python", "-m", "experiment.runner"]