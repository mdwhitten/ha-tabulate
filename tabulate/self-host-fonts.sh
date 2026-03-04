#!/bin/sh
# self-host-fonts.sh — download Google Fonts at build time so the browser
# never needs to reach fonts.googleapis.com at runtime.
#
# Usage: sh self-host-fonts.sh <vite-dist-assets-dir>
#   e.g. sh self-host-fonts.sh /build/dist/assets
set -eu

ASSETS_DIR="$1"
FONTS_DIR="$ASSETS_DIR/fonts"
GFONTS_URL="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"

mkdir -p "$FONTS_DIR"

# 1. Fetch the Google Fonts CSS (User-Agent must request woff2 format)
wget -q -O /tmp/gfonts.css \
  --header="User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  "$GFONTS_URL"

echo "Google Fonts CSS downloaded ($(wc -c < /tmp/gfonts.css) bytes)"

# 2. Extract woff2 URLs into a file (one per line)
#    busybox grep -o works; match url(...woff2) and strip the url() wrapper
grep -o 'url([^)]*\.woff2)' /tmp/gfonts.css | sed 's/^url(//;s/)$//' > /tmp/font-urls.txt

echo "Found $(wc -l < /tmp/font-urls.txt) font URLs"

# 3. Download each font and build a sed script to rewrite URLs
> /tmp/sed-script.txt
i=0
while IFS= read -r url; do
  filename="font-${i}.woff2"
  echo "  Downloading $filename from $url"
  wget -q -O "$FONTS_DIR/$filename" "$url"
  # Build sed substitution — use | as delimiter since URLs contain /
  printf 's|%s|./fonts/%s|g\n' "$url" "$filename" >> /tmp/sed-script.txt
  i=$((i + 1))
done < /tmp/font-urls.txt

# 4. Apply all URL rewrites to produce local @font-face CSS
sed -f /tmp/sed-script.txt /tmp/gfonts.css > /tmp/local-fonts.css

# 5. Strip the external @import from every compiled CSS bundle
for css in "$ASSETS_DIR"/*.css; do
  sed -i 's|@import url([^)]*fonts\.googleapis\.com[^)]*);||g' "$css"
done

# 6. Prepend the local @font-face rules to each CSS bundle
for css in "$ASSETS_DIR"/*.css; do
  cat /tmp/local-fonts.css "$css" > "${css}.tmp" && mv "${css}.tmp" "$css"
done

echo "Self-hosted $(ls "$FONTS_DIR" | wc -l) font files into $FONTS_DIR"
