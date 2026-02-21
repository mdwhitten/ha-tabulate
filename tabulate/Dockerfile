ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.19
FROM node:20-alpine AS frontend-builder

# Clone and build the React frontend
RUN apk add --no-cache git
RUN git clone --depth 1 https://github.com/mdwhitten/tabulate.git /build
WORKDIR /build
ENV NODE_ENV=development
RUN npm ci && npx tsc -b && npx vite build

# ── Final image ──────────────────────────────────────────────────────────────
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    nginx \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    py3-pip \
    py3-numpy \
    py3-pillow \
    jpeg-dev \
    zlib-dev \
    libheif-dev \
    build-base \
    python3-dev \
    curl

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copy backend from the tabulate repo
COPY --from=frontend-builder /build/backend /app

# Copy built frontend
COPY --from=frontend-builder /build/dist /app/frontend

# Copy root filesystem (s6 services, nginx config, run scripts)
COPY rootfs /

# Create data directory
RUN mkdir -p /data/images

WORKDIR /app
