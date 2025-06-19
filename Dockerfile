# syntax=docker/dockerfile:1

# ===== Base Image =====
FROM python:3.12-alpine

# ===== Environment Vars =====
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH="/home/django/.local/bin:$PATH"  

# ===== System Setup =====
WORKDIR /app

# ===== Install system dependencies =====
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    build-base \
    linux-headers \
    libpq \
    curl \
    bash \
    netcat-openbsd \
    && adduser -D django

# ===== Switch to user before install =====
USER django

# ===== Install Python dependencies =====
COPY --chown=django:django requirements.txt .
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# ===== Copy source code =====
COPY --chown=django:django . .

# ===== Expose port =====
EXPOSE 8000

# ===== Default command =====
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]