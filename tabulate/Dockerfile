ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.19
FROM node:20-alpine AS frontend-builder

ARG TABULATE_VERSION=v1.4.0

# Clone the React frontend at a pinned release tag
RUN apk add --no-cache git
RUN git clone --depth 1 --branch ${TABULATE_VERSION} https://github.com/mdwhitten/tabulate.git /build
WORKDIR /build

# Install deps with yarn (npm crashes under QEMU emulation on HA builder)
RUN corepack enable && yarn install

# Build frontend (tsc type-check then vite bundle)
RUN yarn tsc -b && yarn vite build

# Self-host Google Fonts to avoid render-blocking external CSS @import.
# Tablets in HA ingress can stall 30+ seconds waiting for fonts.googleapis.com.
# Fetches the CSS dynamically so we always get current woff2 URLs from Google.
COPY self-host-fonts.sh /tmp/self-host-fonts.sh
RUN sh /tmp/self-host-fonts.sh /build/dist/assets

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
    curl \
    jq

# Install Python dependencies in a virtual environment
# (--system-site-packages reuses apk-installed numpy/pillow to avoid rebuilding)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# pymupdf has no musllinux wheels, so pip builds from source on Alpine.
# The build's C++ binding generator (mupdfwrap.py) loads libclang at runtime.
RUN apk add --no-cache --virtual .pymupdf-build-deps clang-dev

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt \
    && apk del .pymupdf-build-deps

# Copy backend from the tabulate repo
COPY --from=frontend-builder /build/backend /app

# Copy built frontend
COPY --from=frontend-builder /build/dist /app/frontend

# Copy root filesystem (s6 services, nginx config, run scripts)
COPY rootfs /

# Create data directory
RUN mkdir -p /data/images

WORKDIR /app
