FROM python:3.12-slim

WORKDIR /app

# Install dependencies first — separate layer so Docker cache doesn't
# invalidate on every code change, only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
