# ha-tabulate — Developer Context

Home Assistant add-on wrapper for [Tabulate](https://github.com/mdwhitten/tabulate). Packages the React + FastAPI app as an HA ingress add-on with Docker multi-arch images.

## Repo Structure

```
repository.yaml          # HA add-on repository metadata
tabulate/
  config.yaml            # Add-on manifest — name, version, arch, ingress, options
  build.yaml             # Base images per architecture (aarch64, amd64)
  CHANGELOG.md           # User-facing changelog (shown in HA UI)
  Dockerfile             # Multi-stage: clone tabulate repo → build frontend → assemble image
  requirements.txt       # Python dependencies (FastAPI, aiosqlite, anthropic, etc.)
  rootfs/                # s6-overlay service scripts + nginx config
.github/workflows/
  publish.yaml           # Builds & pushes Docker images on GitHub release
  test.yaml              # Verifies Docker build on push/PR
```

## How the App Code Gets In

The Dockerfile clones `https://github.com/mdwhitten/tabulate.git` at a **pinned release tag** (shallow, `--depth 1`) at build time. The tag is set via the `TABULATE_VERSION` build arg in the Dockerfile (e.g. `v1.0.0`). It is NOT a submodule.

## Architecture

- **Frontend build**: `node:20-alpine` stage — `yarn install && yarn tsc -b && yarn vite build`
- **Runtime**: HA base Python 3.12 Alpine image with nginx, Tesseract OCR, and Python venv
- **Services**: s6-overlay runs nginx (serves frontend, proxies `/api`) + uvicorn (FastAPI backend)
- **Data**: Persisted to `/data/` (SQLite DB + receipt images) via HA `addon_config:rw` mount

## Releasing a New Version

1. **Bump `TABULATE_VERSION`** in `tabulate/Dockerfile` to the new upstream release tag (e.g. `v1.1.0`)
2. **Bump version** in `tabulate/config.yaml` (the `version:` field)
3. **Update changelog** in `tabulate/CHANGELOG.md` — add a new section at the top with the version number and describe changes under Added/Changed/Fixed headings
4. **Commit and push** all files to main
5. **Create a GitHub release** with tag `v<version>` (e.g. `v0.2.0`):
   ```
   gh release create v0.2.0 --title "v0.2.0" --notes "<release notes>"
   ```
6. The `publish.yaml` workflow triggers automatically, building and pushing `ghcr.io/mdwhitten/ha-tabulate-{amd64,aarch64}` images

**Important**: The version in `config.yaml` must match the release tag (minus the `v` prefix). HA uses `config.yaml` version to detect updates.

## Build Notes

- Uses **yarn** instead of npm because npm crashes under QEMU emulation on the HA multi-arch builder
- Python venv uses `--system-site-packages` to reuse apk-installed numpy/pillow (avoids slow native compilation)
- Two architectures: `amd64` and `aarch64` (covers x86 servers and Raspberry Pi)

## Upstream Tabulate API Reference

Source: [github.com/mdwhitten/tabulate](https://github.com/mdwhitten/tabulate). All endpoints are prefixed with `/api`. No auth layer — relies on HA ingress. CORS is fully open (`*`).

### Health & Diagnostics

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Returns `{ status, version }` |
| GET | `/api/diagnose` | Checks tesseract, pytesseract, pillow, HEIC support, data dir, Anthropic key |

### Receipts (`/api/receipts`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/receipts/upload` | **Upload receipt image** — multipart form: `file` (image), optional `store_name_hint` (string), optional `crop_corners` (JSON `[[x,y],…]` fractions). Runs OCR + Claude Vision categorization. Returns `ProcessingResult` with receipt_id, parsed items, totals, thumbnail. |
| GET | `/api/receipts` | List receipts (paginated: `?limit=50&offset=0`). Returns summary with id, store, date, total, item_count, status. |
| GET | `/api/receipts/{id}` | Full receipt with line items |
| POST | `/api/receipts/{id}/save` | Apply corrections and/or approve. Body: `{ corrections, price_corrections, name_corrections, manual_total, receipt_date, store_name, new_items, deleted_item_ids, approve }`. `approve=true` → status='verified'. |
| DELETE | `/api/receipts/{id}` | Delete receipt + image files |
| GET | `/api/receipts/{id}/image` | Serve original JPEG |
| GET | `/api/receipts/{id}/thumbnail` | Serve thumbnail (falls back to full image) |
| GET | `/api/receipts/{id}/detect-edges` | Edge detection on stored image → `{ corners: [[x,y],…] }` |
| POST | `/api/receipts/detect-edges-raw` | Edge detection on uploaded image (multipart `file`, no DB save) |
| POST | `/api/receipts/{id}/crop` | Crop stored image in-place. Body: `{ corners: [[x,y],…] }` |
| GET | `/api/receipts/check-duplicates` | `?total=&receipt_date=&exclude_id=` → matching receipts |
| GET | `/api/receipts/diagnose` | Receipt subsystem diagnostics |

**Upload details**: Accepts JPEG, PNG, HEIC, WebP, BMP, TIFF. Auto-normalizes EXIF orientation, re-encodes as JPEG. Saves to `/data/images/{uuid}.jpg`. Generates thumbnail. nginx limit: 20 MB, 120 s timeout.

### Items (`/api/items`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| PATCH | `/api/items/{id}/category` | Update item category. Body: `{ category }` |
| GET | `/api/items/mappings` | List learned mappings (paginated: `?limit=50&offset=0&search=&category=`). Returns `{ total, items }`. |
| PATCH | `/api/items/mappings/{id}/category` | Update mapping category. Body: `{ category }` |
| DELETE | `/api/items/mappings/{id}` | Delete learned mapping |
| GET | `/api/items/categories` | List category name strings |

### Categories (`/api/categories`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/categories` | List all categories with id, name, color (hex), icon (emoji), is_builtin, is_disabled, sort_order |
| POST | `/api/categories` | Create custom category. Body: `{ name, color?, icon? }` |
| PATCH | `/api/categories/{id}` | Update category. Body: `{ name?, color?, icon?, is_disabled? }`. Built-ins: only is_disabled is mutable. |
| DELETE | `/api/categories/{id}` | Delete custom category (reassigns items to "Other"). Built-ins protected. |

### Trends (`/api/trends`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/trends/monthly` | Monthly spending by category (`?months=6`, range 1-24). Only verified receipts. |
| GET | `/api/trends/monthly/{year}/{month}` | Single month detail breakdown by category + store |
| GET | `/api/trends/stores` | Store breakdown (`?months=3`, range 1-12) — receipt_count, total_spent, avg_trip |
| GET | `/api/trends/summary` | Dashboard: month_total, receipt_count, items_learned, avg_trip |

### Key Details

- **Receipt statuses**: `pending` (draft) → `verified` (finalized via save with `approve=true`)
- **Categorization sources**: `ai` (Claude Vision) or `manual` (user-corrected)
- **Item mappings**: Learned rules (normalized_key → category) for auto-categorization of future receipts
- **Data**: SQLite at `/data/tabulate.db`, images at `/data/images/`
