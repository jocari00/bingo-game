FROM python:3.12-slim

# Install system deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Set PYTHONPATH so the `src` layout is importable inside the container
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Copy requirements first for caching
COPY requirements.txt /app/
RUN python -m pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app

# Expose nothing in particular; this is a CLI app

# Default command: run tests to validate the image. For interactive demo, override with
# `docker run -it --rm <image> python -m game.main`
CMD ["python", "-m", "pytest", "-q"]
