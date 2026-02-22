# Changelog

## 1.0.0

### Added
- Category picker redesigned as a popover with search, matching the emoji picker style
- Distinct color palette for custom categories so they don't all default to the same color
- Mobile modal editor now opens on approved receipts for category editing

### Fixed
- Docker build switched from npm to yarn to fix silent install failures on Alpine/QEMU
- Removed autoFocus from emoji picker search input to prevent keyboard pop-up on mobile

### Changed
- Upgraded upstream Tabulate from v1.0.0 to v1.1.0

## 0.2.3

### Added
- Receipt crop flow with pre-upload and re-crop support
- Average amount column in trends breakdown table
- URL routing with browser history support
- Search and status filters on All Receipts list

### Changed
- Upgraded to React 19 and Tailwind CSS 4
- Pinned Docker build to upstream Tabulate v1.0.0 release tag

### Fixed
- Stacked bar chart uses clipPath for uniform corner rounding
- Y-axis scaling uses finer steps to fill chart area
- Scan button alignment and popup menu cutoff on mobile
- Desktop table padding restored to appropriate values

## 0.2.2

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

## 0.2.1

### Fixed
- Custom category colors and icons now display correctly in spending charts and trend graphs
- New category form auto-scrolls and focuses the name input so the user can see the new entry

### Changed
- Approved receipts now allow category changes (prices, names, and item add/delete remain locked)
- Receipts stat card on the dashboard links to the All Receipts page

## 0.2.0

### Added
- **Save / Approve split** — save receipt edits as drafts without finalizing; approve when ready to lock
- **Swipe-to-delete** on line item rows (mobile touch support)
- **Emoji icon picker** for category icons with search, grouped by grocery section
- **Paginated learned items** with server-side search and category filtering
- Unsaved changes guard on navigation and browser back/forward
- Negative adjustment support in receipt verify bar
- Date validation required before saving receipts

### Changed
- Categorization engine switched from Sonnet to Haiku for significantly faster item classification
- Batch DB writes for learned item mappings (single executemany instead of sequential inserts)
- Terminology: "Verified" → "Approved", "Total Verified" → "Total Balanced"
- Camera icon replaces Upload icon in sidebar and topbar scan button

### Fixed
- ASI bug with window globals (use local variable)
- Rules of Hooks violation (useMemo before early returns)

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
