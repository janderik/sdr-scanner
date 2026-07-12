FROM python:3.11-slim

RUN apt-get update && apt-get install -y librtlsdr-dev libhackrf-dev libusb-1.0-0-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "cli.py"]
