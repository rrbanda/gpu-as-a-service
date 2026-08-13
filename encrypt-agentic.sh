#!/bin/bash
# Encrypts agentic-slides.html for password-protected GitHub Pages deployment.
# The password is NEVER committed to git — share it out-of-band (Slack, email, etc.).
#
# Usage:
#   ./encrypt-agentic.sh                  # prompts for password interactively
#   STATICRYPT_PASSWORD=xyz ./encrypt-agentic.sh  # uses env var (CI/CD)
#
# Output: agentic/index.html (the file GitHub Pages serves at /gpu-as-a-service/agentic/)

set -euo pipefail

if [ ! -f agentic-slides.html ]; then
  echo "Error: agentic-slides.html not found."
  exit 1
fi

npx staticrypt agentic-slides.html \
  --directory agentic \
  --config false \
  --short \
  --remember 7 \
  --template-title "Agentic AI Architecture Deep-Dive — Red Hat" \
  --template-instructions "Enter the presentation password to continue." \
  --template-color-primary "#EE0000" \
  --template-color-secondary "#151515"

# staticrypt outputs the filename as-is; rename to index.html for clean URLs
if [ -f agentic/agentic-slides.html ]; then
  mv agentic/agentic-slides.html agentic/index.html
fi

echo ""
echo "Encrypted → agentic/index.html"
echo "Will be served at: https://rrbanda.github.io/gpu-as-a-service/agentic/"
echo "DO NOT commit the password anywhere."
