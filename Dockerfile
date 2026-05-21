FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# GDAL is required by django.contrib.gis for PostGIS support
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p .cache/django_cache locale/kn/LC_MESSAGES

EXPOSE 8000

CMD ["gunicorn", "SmartTransportSystem.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
