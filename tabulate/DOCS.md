# Tabulate — Documentation

## Overview

Tabulate is a self-hosted grocery receipt tracker. Upload a photo of your receipt and AI will extract the store, date, items, and prices — then categorize everything automatically.

## How it works

1. **Scan** — Upload or photograph a grocery receipt
2. **Extract** — Tesseract OCR reads the text; Claude Vision enriches the data
3. **Review** — Verify items, correct categories, and confirm the total
4. **Track** — See spending trends by month and category over time

## Configuration

### Required

- **Anthropic API Key** — Get one at [console.anthropic.com](https://console.anthropic.com/). This powers the AI vision model that enriches OCR results and categorizes items.

### Data storage

All data (SQLite database + receipt images) is stored in the add-on's persistent `/data` directory. Data survives add-on restarts and updates.

## Accessing the UI

Once started, Tabulate appears in your Home Assistant sidebar (via ingress). Click the receipt icon to open the app.

## Troubleshooting

- **"OCR failed"** — The receipt image may be too blurry or dark. Try a clearer photo.
- **"Upload failed"** — Check that your Anthropic API key is set correctly in the add-on configuration.
- **Items miscategorized** — Correct them in the review screen. Tabulate learns from your corrections and applies them to future scans.
