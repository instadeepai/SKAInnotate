# Using Python runtime as a parent image
FROM python:3.10-slim AS base

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -v --no-cache-dir -r /app/requirements.txt

COPY core/backend /app/core/backend

COPY core/frontend/build /app/core/frontend/build  

# Add a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Environment variables
ENV PYTHONPATH=/app:/app/core/backend
ENV PATH=/root/.local/bin:$PATH
ENV HOST=0.0.0.0
ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "core.backend.app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
