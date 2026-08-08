# ---- Stage 1: Builder ----
# This stage installs everything and prepares the app.
# It will NOT be part of the final image.
FROM python:3.12-slim AS builder
WORKDIR /app

# Copy requirements FIRST (changes to requirements.txt invalidate cache)
COPY requirements.txt ./

# Install dependencies into a virtual environment
# This layer is cached as long as requirements.txt doesn't change
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# THEN copy application code (changes to app code don't invalidate pip install layer)
# Copy only the directories needed for runtime, not test files or unnecessary files
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

# ---- Stage 2: Runtime ----
# This is the final image. It starts fresh -- nothing from Stage 1
# exists here unless we explicitly COPY it.
FROM python:3.12-slim
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the application code (not tests, build artifacts, etc.)
COPY --from=builder /app/app ./app
COPY --from=builder /app/alembic ./alembic
COPY --from=builder /app/alembic.ini ./
COPY --from=builder /app/scripts ./scripts

# Create a non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser
USER appuser

# Expose the port the FastAPI app listens on
EXPOSE 8000

# Health check: verify the service is responding to /live endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/live || exit 1

# The command that runs when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
