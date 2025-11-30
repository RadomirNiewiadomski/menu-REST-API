FROM python:3.12-slim-bookworm

# Copy uv from the official image (trick to avoid manual installation)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT="/usr/local"

WORKDIR /app

# Copy dependency files first (to leverage Docker cache layers)
COPY pyproject.toml uv.lock ./

ARG DEV=false

RUN if [ "$DEV" = "true" ]; then \
        uv sync --frozen; \
    else \
        uv sync --frozen --no-dev; \
    fi

# Copy the rest of the application code
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" django-user
USER django-user

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]
