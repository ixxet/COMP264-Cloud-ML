FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AWS_EC2_METADATA_DISABLED=true

WORKDIR /app

COPY requirements-container.txt .
RUN pip install --no-cache-dir -r requirements-container.txt

COPY app.py .
COPY chalicelib ./chalicelib
COPY .chalice ./.chalice

EXPOSE 8000

CMD ["chalice", "local", "--host", "0.0.0.0", "--port", "8000"]
