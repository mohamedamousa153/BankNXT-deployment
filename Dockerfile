 FROM python:3.9-slim

WORKDIR /app

# Install dependencies first for better caching
COPY backend/requirements.txt /app/backend/
WORKDIR /app/backend
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy the rest of the application
WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend

# OpenShift compatibility: non-root users must be able to write to the backend directory
# (specifically for sqlite dashboard.db creation at runtime)
RUN chgrp -R 0 /app/backend && \
    chmod -R g=u /app/backend

# Switch to a non-root user (arbitrary UID support)
USER 1001

# Expose non-privileged port
EXPOSE 8080

# Initialize database and start the server on port 8080
WORKDIR /app/backend
CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8080"]
