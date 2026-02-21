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

## Add-ons in this repository

### [Tabulate](./tabulate)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

Grocery receipt tracker with OCR + AI categorization.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
