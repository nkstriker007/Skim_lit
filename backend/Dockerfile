FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# requirements.txt accessible from root context
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only backend code into /app
COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
