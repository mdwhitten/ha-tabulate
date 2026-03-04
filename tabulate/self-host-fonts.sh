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
wget -q -O /tmp/gfonts.css --header="User-Agent: Mozilla/5.0 Chrome/120" "$GFONTS_URL"

# 2. Extract woff2 URLs into a file (one per line)
#    Works with busybox grep (no -P needed)
sed -n 's|.*url(\([^)]*\.woff2\)).*|\1|p' /tmp/gfonts.css > /tmp/font-urls.txt

# 3. Download each font and build a sed script to rewrite URLs
cp /tmp/gfonts.css /tmp/local-fonts.css
i=0
while IFS= read -r url; do
  filename="font-${i}.woff2"
  wget -q -O "$FONTS_DIR/$filename" "$url"
  # Build sed substitution — use | as delimiter since URLs contain /
  printf 's|%s|./fonts/%s|g\n' "$url" "$filename" >> /tmp/sed-script.txt
  i=$((i + 1))
done < /tmp/font-urls.txt

# 4. Apply all URL rewrites to produce local CSS
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
