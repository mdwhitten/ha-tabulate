# Changelog

## 1.5.1

### Fixed
- Add missing pymupdf dependency required for PDF receipt upload support added in v1.5.0
- Docker build failure on Alpine (aarch64) — pymupdf source compilation needs libclang for C++ binding generation

### Changed
- Update-upstream workflow now auto-syncs requirements.txt with upstream packages
- PR validation workflow now checks that all upstream Python packages are present locally

## 1.5.0


### Added
- PDF receipt upload support — single and multi-page PDFs are converted to JPEG via  for thumbnails and Vision enrichment
- Direct text extraction from text-based PDFs, skipping Tesseract OCR for faster processing
- Frontend skips crop stage for PDF uploads since digital documents don't need perspective correction

### Fixed
- Trends router tests used hardcoded Feb 2026 dates causing failures in later months — now use dynamic dates relative to today

### Changed
- Upgraded upstream Tabulate from v1.3.1 to v1.4.0


## 1.4.2


### Fixed
- Blank screen for ~30 seconds on tablets — self-host Google Fonts at build time to eliminate render-blocking external CSS @import that stalls in HA ingress iframe WebViews

## 1.4.1


### Added
- Edit button on verified receipts — unlocks date, store name, and categories for correction while keeping items, prices, and totals locked
- Categorization failure detection with retry banner on receipt review
- GitHub Actions workflow for Playwright E2E tests with artifact upload
- E2E test coverage for editing approved receipts (click Edit, change fields, save) on desktop and mobile
- Mobile E2E test suites for navigation (hamburger menu), All Receipts (hidden columns, compact badges), Trends (bottom sheet category drill-down), and Learned Items (swipe-to-delete)
- Playwright  (Pixel 5) project for mobile viewport E2E testing
- Desktop-only skip guards on sidebar navigation and inline expansion tests that fail at mobile viewport

### Changed
- Verified receipts are now fully read-only by default (categories included); editing requires explicitly tapping Edit

### Fixed
- Price corrections could modify line items belonging to a different receipt — query now scoped to 
- Receipt date field accepted arbitrary strings (e.g. ) that broke trend queries — now validated as ISO 
- Empty/whitespace-only store name was stored as  instead of being treated as null
- New items accepted nonexistent or disabled categories — now validated against the categories table
- Negative manual total accepted and stored — now rejected with 422
- SQL injection vector in image serving helper — column name now validated against a whitelist
- SQL fragment interpolation in receipt save endpoint replaced with parameterized query
- Wildcard CORS no longer sends credentials; added  env var for explicit origin lists
- API key prefix no longer leaked in  response — only reports presence
- File upload now validates Content-Type against allowed image types and enforces 20 MB size cap server-side
- Backend port in Docker Compose bound to  so it's not exposed to the network
- Crop endpoint body changed from unvalidated  to a Pydantic model with typed  field
- Image file serving now verifies resolved paths are contained within  to prevent path traversal
- Trends expanded-item column layout misaligned and scroll lock bug on mobile
- Empty footer bar visible on mobile for verified receipts with no actions

- Upgraded upstream Tabulate from v1.3.0 to v1.3.1


## 1.4.0


### Added
- Category item drill-down in trends view — tap a category to see its individual items
- Mobile overflow menu (•••) on receipt review topbar with Rescan, Save, and Delete actions
- Green approve icon button in mobile topbar for quick one-tap approval

### Changed
- Topbar height increased for easier tapping on mobile (h-12 → h-14)
- Back button enlarged with visible border outline for better mobile tap target
- Receipt review footer streamlined — Cancel/Close removed (back button handles navigation), Rescan/Delete hidden on mobile (moved to topbar overflow), Save/Approve stretch full-width on small screens
- All item mappings (both AI and manual corrections) are now deferred until receipt approval — cancelling or deleting an unreviewed receipt no longer leaves orphaned mappings behind

### Fixed
- Receipt date field not tappable on mobile when empty
- Date field now stays visibly editable while receipt is unverified
- Bottom padding added so content doesn't butt against the tab bar in embedded mode
- Category source badge (AI/Manual/Learned) now updates to Manual immediately when the user overrides a category, instead of waiting until save

- Upgraded upstream Tabulate from v1.2.6 to v1.3.0


## 1.3.4


### Fixed
- Learned item categorization no longer matches wrong category from short generic seed mappings (e.g. milk seed matching Taste of Thai Coconut Milk)
- Swipe-to-delete on learned items table now reveals red across the full row width instead of being cramped into a narrow strip

### Changed
- Upgraded upstream Tabulate from v1.2.5 to v1.2.6


## 1.3.3


### Fixed
- Scan button no longer extends outside the bottom tab bar in embedded mode
- Status column on mobile receipts list now shows a compact icon-only badge instead of overflowing offscreen
- Swipe-to-delete on learned items table no longer shows fragmented red strips across cells on tablet — only the delete action column reveals the indicator
- Disabled categories are excluded from AI categorization prompts, learned mapping lookups, and the category picker dropdown

### Changed
- Upgraded upstream Tabulate from v1.2.4 to v1.2.5


## 1.3.2


### Fixed
- Backend startup crash when item_mappings table contains both space-containing and space-free normalized keys (e.g. ground beef and groundbeef), causing a UNIQUE constraint failure

### Changed
- Upgraded upstream Tabulate from v1.2.3 to v1.2.4


## 1.3.1


### Fixed
- Item mapping lookup now ignores spaces so OCR variants like KS Steakstrip and KSSteakstrip match the same rule

### Removed
- Home Assistant theme awareness (accent color and dark mode detection from parent HA iframe) — caused visual regressions

### Changed
- Upgraded upstream Tabulate from v1.2.2 to v1.2.3


## 1.3.0


### Added
- Home Assistant theme awareness — accent color and dark/light mode are read from the parent HA iframe
- Delete functionality for learned item mapping rules
- Auto-release and PR validation CI workflows
- Notify HA add-on repo on upstream release

### Fixed
- Duplicate item mappings caused by friendly names leaking into raw_name key
- Scan button alignment and Avg column header alignment

### Changed
- Upgraded upstream Tabulate from v1.2.1 to v1.2.2


## 1.2.0


### Fixed
- Changing a learned item's category now updates the mappings table instead of misrouting to line items
- Category filter chips on the Learned Items page now display custom category icons and colors

### Changed
- Upgraded upstream Tabulate from v1.2.0 to v1.2.1


## 1.1.0

### Added
- Duplicate receipt detection matching on total and date before upload
- Styled DuplicateWarningModal replacing browser `window.confirm`
- Backend test suite for categorization service (38 tests)
- CI workflow running backend and frontend tests on push and PR

### Fixed
- AI categorization no longer overrides manual or learned category mappings

### Changed
- Upgraded upstream Tabulate from v1.1.0 to v1.2.0

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
