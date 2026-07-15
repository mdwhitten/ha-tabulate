# Tabulate — Home Assistant Add-on Repository

Self-hosted grocery receipt tracker, packaged as a Home Assistant add-on.

Scan receipts with your phone, let OCR + Claude Vision extract items and categories, then review and verify your spending — all from the Home Assistant sidebar.

## Installation

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**
2. Click the **three-dot menu** (top right) → **Repositories**
3. Add this URL: `https://github.com/mdwhitten/ha-tabulate`
4. Find **Tabulate** in the store and click **Install**
5. In the add-on **Configuration** tab, set your Anthropic API key
6. Start the add-on — it will appear in your sidebar

## Home Assistant integration (actions)

Alongside the add-on, this repository ships a companion **custom integration**
(`custom_components/tabulate`) that adds a first-class Home Assistant action,
`tabulate.add_receipt`. It lets automations — or external callers like an Apple
Shortcut — hand a receipt image to Tabulate through Home Assistant's own
authenticated API, without going through ingress.

### Install (HACS)

1. In HACS → **Integrations** → three-dot menu → **Custom repositories**, add
   `https://github.com/mdwhitten/ha-tabulate` with category **Integration**.
2. Install **Tabulate**, then restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration → Tabulate**. It
   auto-detects the running add-on; if it can't, enter the host and port
   (default `8099`) manually.

### The `tabulate.add_receipt` action

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `image_base64` | yes | — | Receipt image, base64-encoded (JPEG/PNG/WEBP/TIFF/HEIC/PDF, ≤ 20 MB). A `data:` URI prefix is tolerated. |
| `filename` | no | `receipt.jpg` | File name sent with the upload. |
| `content_type` | no | `image/jpeg` | MIME type of the image. |
| `store_name_hint` | no | — | Hint to help identify the store. |
| `wait_for_processing` | no | `true` | If `true`, waits for OCR + AI processing and returns the parsed receipt. If `false`, uploads in the background and returns immediately. |

Tabulate processes receipts **synchronously** (OCR + Claude Vision +
categorization can take seconds to ~120s). With `wait_for_processing: true` the
action returns the parsed result; with `false` it returns `{ "queued": true }`
right away so a caller with a short timeout won't fail — the receipt still lands
in the Tabulate UI for review shortly after.

### Apple Shortcuts recipe

Scan with the built-in **Scan Document** action (VisionKit), then **Get Contents
of URL**:

- **URL**: `https://<your-ha>/api/services/tabulate/add_receipt?return_response`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <long-lived-access-token>`
- **Request Body** (JSON):
  ```json
  {
    "image_base64": "<Base64 Encode of the scanned image>",
    "wait_for_processing": false
  }
  ```

Use `wait_for_processing: false` in a Shortcut to avoid its request timing out;
set it to `true` (and read `service_response`) when you want the parsed store,
total, and line items back.

## Add-ons in this repository

### [Tabulate](./tabulate)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

Grocery receipt tracker with OCR + AI categorization.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
