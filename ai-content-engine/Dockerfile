FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 2000

# Use gunicorn with uvicorn workers for production, bind to port 2000
CMD ["gunicorn", "app.main:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:2000", "--workers", "2"]
