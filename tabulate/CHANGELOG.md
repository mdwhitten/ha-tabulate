# Changelog

## 0.1.1

### Fixed
- Receipt list failing to load in HA ingress mode (duplicate nginx location block)

### Added
- **Verbose logging** option in addon configuration — enables DEBUG-level logs and uvicorn access logs for troubleshooting
- Structured logging across the entire backend (replaces ad-hoc print statements)
- HTTP request middleware that logs all 4xx/5xx responses with method, path, status, and latency
- Defensive NULL handling in receipt list serialization

### Changed
- API key field is now masked as a password in the addon configuration UI

## 0.1.0

- Initial release
- Receipt upload with crop and edge detection
- Two-pass OCR (Tesseract + Claude Vision)
- AI-powered item categorization with learning
- Spending trends dashboard
- Home Assistant ingress integration
