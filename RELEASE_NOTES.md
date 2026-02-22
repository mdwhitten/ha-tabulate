## v0.2.2

### Added
- Bottom tab bar navigation when running inside Home Assistant ingress (replaces sidebar for mobile-friendly navigation)
- Mobile bottom-sheet modal for editing line items (replaces cramped inline table editing on small screens)

### Changed
- Receipts list now sorted by receipt date instead of upload time
- Categories under $5 hidden in per-category bar chart to reduce clutter
- Bottom tab bar consolidated to 3 section groups (Overview, Receipts, Manage) with popup menus
- Updated FastAPI from 0.115.5 to 0.129.2
- Updated Uvicorn from 0.32.1 to 0.41.0
- Updated Anthropic SDK from 0.40.0 to 0.83.0
- Updated Pydantic from 2.10.3 to 2.12.5
- Updated aiosqlite from 0.20.0 to 0.22.1
- Updated python-multipart from 0.0.12 to 0.0.22

### Fixed
- Category matching now prefers most specific learned mapping (e.g., "coconut milk" → Pantry wins over "milk" → Dairy)
- Status badge no longer wraps to two lines on mobile
