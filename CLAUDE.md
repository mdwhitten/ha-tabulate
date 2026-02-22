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
