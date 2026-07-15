"""Constants for the Tabulate integration."""

from __future__ import annotations

DOMAIN = "tabulate"

# Slug of the companion Tabulate add-on, used to resolve its internal
# Supervisor-network hostname.
ADDON_SLUG = "tabulate"

# The add-on's nginx listens on 8099 (ingress port); the FastAPI backend is
# loopback-bound, so 8099 is the only port reachable from HA core.
DEFAULT_PORT = 8099

CONF_HOST = "host"
CONF_PORT = "port"

# Service (action) exposed to Home Assistant.
SERVICE_ADD_RECEIPT = "add_receipt"

# Service field names.
ATTR_IMAGE_BASE64 = "image_base64"
ATTR_FILENAME = "filename"
ATTR_CONTENT_TYPE = "content_type"
ATTR_STORE_NAME_HINT = "store_name_hint"
ATTR_WAIT_FOR_PROCESSING = "wait_for_processing"

DEFAULT_FILENAME = "receipt.jpg"
DEFAULT_CONTENT_TYPE = "image/jpeg"

# Tabulate ingest endpoint (multipart/form-data, file field "file").
UPLOAD_PATH = "/api/receipts/upload"
# Lightweight endpoint used to verify connectivity during config flow.
PING_PATH = "/api/receipts"

# Mirrors the add-on's nginx client_max_body_size / upstream _MAX_UPLOAD_BYTES.
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

# Upstream processing is synchronous (OCR + Claude Vision + categorization) and
# nginx caps the proxied response at proxy_read_timeout 120s.
UPLOAD_TIMEOUT = 120
PING_TIMEOUT = 10
