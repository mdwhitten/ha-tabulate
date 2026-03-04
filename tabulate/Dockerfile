ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.19
FROM node:20-alpine AS frontend-builder

ARG TABULATE_VERSION=v1.3.1

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
RUN FONTS_DIR=/build/dist/assets/fonts && mkdir -p "$FONTS_DIR" \
    # Download Inter (latin, 300/400/500/600)
    && wget -q -O "$FONTS_DIR/inter-300.woff2" "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuOKfMZs.woff2" \
    && wget -q -O "$FONTS_DIR/inter-400.woff2" "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZs.woff2" \
    && wget -q -O "$FONTS_DIR/inter-500.woff2" "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuI6fMZs.woff2" \
    && wget -q -O "$FONTS_DIR/inter-600.woff2" "https://fonts.gstatic.com/s/inter/v18/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZs.woff2" \
    # Download JetBrains Mono (latin, 400/500)
    && wget -q -O "$FONTS_DIR/jetbrains-mono-400.woff2" "https://fonts.gstatic.com/s/jetbrainsmono/v21/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOTk6OThhvA.woff2" \
    && wget -q -O "$FONTS_DIR/jetbrains-mono-500.woff2" "https://fonts.gstatic.com/s/jetbrainsmono/v21/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTClOTk6OThhvA.woff2" \
    # Strip the external @import from compiled CSS and prepend local @font-face rules
    && for css in /build/dist/assets/*.css; do \
         sed -i 's|@import url([^)]*fonts\.googleapis\.com[^)]*);||g' "$css"; \
       done \
    && cat > /tmp/fonts.css <<'FONTCSS'
@font-face { font-family: 'Inter'; font-style: normal; font-weight: 300; font-display: swap; src: url(./fonts/inter-300.woff2) format('woff2'); }
@font-face { font-family: 'Inter'; font-style: normal; font-weight: 400; font-display: swap; src: url(./fonts/inter-400.woff2) format('woff2'); }
@font-face { font-family: 'Inter'; font-style: normal; font-weight: 500; font-display: swap; src: url(./fonts/inter-500.woff2) format('woff2'); }
@font-face { font-family: 'Inter'; font-style: normal; font-weight: 600; font-display: swap; src: url(./fonts/inter-600.woff2) format('woff2'); }
@font-face { font-family: 'JetBrains Mono'; font-style: normal; font-weight: 400; font-display: swap; src: url(./fonts/jetbrains-mono-400.woff2) format('woff2'); }
@font-face { font-family: 'JetBrains Mono'; font-style: normal; font-weight: 500; font-display: swap; src: url(./fonts/jetbrains-mono-500.woff2) format('woff2'); }
FONTCSS
    && for css in /build/dist/assets/*.css; do \
         cat /tmp/fonts.css "$css" > "$css.tmp" && mv "$css.tmp" "$css"; \
       done

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

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
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
