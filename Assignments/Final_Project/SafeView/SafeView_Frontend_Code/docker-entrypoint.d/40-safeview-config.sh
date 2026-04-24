#!/bin/sh
set -eu

cat > /usr/share/nginx/html/config.js <<EOF
window.SAFEVIEW_API_BASE = "${SAFEVIEW_API_BASE}";
EOF
