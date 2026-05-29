FROM python:3.12-slim

WORKDIR /app

# Install deps in a separate layer — only rebuilds when requirements.txt changes,
# not on every code change. This is the single most impactful Docker optimization.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The /app/data directory is where the Go bridge writes its SQLite DB.
# We create it here so the volume mount has somewhere to land.
RUN mkdir -p /app/data

EXPOSE 3002

CMD ["python", "server.py"]
