FROM python:3.12-slim

WORKDIR /app

# uv install karo
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Dependencies pehle copy karo (layer caching ke liye)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Baaki files copy karo
COPY server.py seed_db.py ./

# Database seed karo (image build ke waqt)
RUN uv run python seed_db.py

# Port expose karo
EXPOSE 8000

# Server start karo (HTTP mode mein)
CMD ["uv", "run", "python", "server.py"]