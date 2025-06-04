FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl 
RUN apt-get install -y --no-install-recommends docker.io 
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client ./client
CMD ["python3", "client/client.py"]