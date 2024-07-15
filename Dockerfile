# Using Python runtime as a parent image
FROM python:3.10-slim AS base

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install -v --no-cache-dir -r /app/requirements.txt

# Copy the backend and frontend directories into the container
COPY core/backend /app/backend
COPY core/frontend /app/frontend

# Set the environment variables
ENV PYTHONPATH=/app/backend:/app/frontend
ENV PATH=/root/.local/bin:$PATH

ENV HOST=0.0.0.0
ENV PORT=8080

# Expose the port for the application
EXPOSE 8080

# Command to run the application
CMD ["gunicorn", "backend.app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker"]
