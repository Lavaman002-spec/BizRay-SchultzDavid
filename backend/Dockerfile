FROM python:3.11-slim

WORKDIR /bizray/backend

# install system dependencies for postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first (for caching)
COPY requirements.txt .

# force reinstall psycopg2-binary even if psycopg3 is in requirements
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycopg2-binary==2.9.9

# copy rest of the source
COPY . .

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
