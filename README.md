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
| `image_base64` | one of these | — | A single receipt image, base64-encoded (JPEG/PNG/WEBP/TIFF/HEIC/PDF, ≤ 20 MB). A `data:` URI prefix is tolerated. |
| `images_base64` | one of these | — | A **list** of base64 images, each added as its own receipt in one call. |
| `filename` | no | `receipt.jpg` | File name sent with the upload. |
| `content_type` | no | `image/jpeg` | MIME type of the image. |
| `store_name_hint` | no | — | Hint to help identify the store. |
| `wait_for_processing` | no | `true` | If `true`, waits for OCR + AI processing and returns the parsed receipt(s). If `false`, uploads in the background and returns immediately. |

Tabulate processes receipts **synchronously** (OCR + Claude Vision +
categorization can take seconds to ~120s). With `wait_for_processing: true` the
action returns the parsed result; with `false` it returns `{ "queued": N }`
right away so a caller with a short timeout won't fail — the receipt still lands
in the Tabulate UI for review shortly after.

For a single image the wait response is the receipt object itself; for
`images_base64` it is `{ "count", "succeeded", "failed", "results": [...] }`.

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

### Multiple images in one Shortcut

A document scan returns a **list** of images, and *Base64 Encode* maps over the
list, giving a list of strings. JSON can't hold binary, so you build an array of
those strings. Two options:

**A. One receipt per image — loop (simplest, works with the HA app's built-in
"Perform Action"):**

1. **Scan Document** → images
2. **Repeat with Each** (Item = each image)
   - **Convert Image** → JPEG → **Base64 Encode**
   - **Perform Action** `tabulate.add_receipt` with dictionary
     `{ "image_base64": «Base64», "wait_for_processing": false }`

**B. Whole batch in one call — build the JSON array, then `images_base64`:**

Binding a Shortcuts *list* into a dictionary's Array field is finicky, so build
the JSON as text (base64 has no characters that need JSON-escaping) and convert:

1. **Repeat with Each** image → **Convert Image** (JPEG) → **Base64 Encode** →
   **Text** `"«Base64»"` (wrap in quotes) → **Add to Variable** `items`
2. **Combine Text** `items` with separator `, `
3. **Text**: `{"images_base64":[«Combined»],"wait_for_processing":false}`
4. **Get Dictionary from Input** (the Text) → **Perform Action**
   `tabulate.add_receipt` with that dictionary

Multi-page scans of a *single* long receipt are different: use **Combine
Images → Vertically** into one image first, then send it as a single
`image_base64`. Large batches are gentler on memory via option A.

### Optional: receipt-summary template

This repo also ships a small **HACS template** (`tabulate.jinja`) — a reusable
Jinja macro for formatting an `add_receipt` response. It's independent of the
integration (the action itself comes from the integration above; the template
is just a display helper). Add the repository to HACS as a **Template** to
install it into `custom_templates/`, then:

```jinja
{% from 'tabulate.jinja' import receipt_summary %}
{{ receipt_summary(response) }}
{# "Trader Joe's — 42.17 · 12 items"  (single receipt) #}
{# "3 receipts added (2 ok, 1 failed)"  (images_base64 batch) #}
```

It accepts either response shape (single receipt or batch summary).

## Add-ons in this repository

### [Tabulate](./tabulate)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

Grocery receipt tracker with OCR + AI categorization.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
