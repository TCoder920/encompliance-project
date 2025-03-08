FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

COPY ./requirements.txt /tmp/

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/wheels -r requirements.txt


FROM python:3.11-slim

# Create a non-root user to run the application
RUN addgroup --system app && \
    adduser --system --group app

WORKDIR /app

# Copy requirements and pre-compiled wheels
COPY --from=requirements-stage /tmp/wheels /wheels
COPY --from=requirements-stage /tmp/requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    # Add any other dependencies required for your app
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application code
COPY ./app /app/app
COPY ./main.py /app/

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER app

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
