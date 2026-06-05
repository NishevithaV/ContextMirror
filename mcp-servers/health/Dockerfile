FROM python:3.13-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends libpq5 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /root_project

# Install dependencies first (separate layer — only re-runs when lock/pyproject change)
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen --no-dev --no-install-project

# Now copy source and install the project itself
COPY . .
RUN uv sync --frozen --no-dev

ENV PATH="/root_project/.venv/bin:$PATH"

EXPOSE 3003

CMD ["python", "app/main.py"]
