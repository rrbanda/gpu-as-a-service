#!/bin/bash
# Encrypts slides.html for password-protected GitHub Pages deployment.
# The password is NEVER committed to git — share it out-of-band (Slack, email, etc.).
#
# Usage:
#   ./encrypt.sh                  # prompts for password interactively
#   STATICRYPT_PASSWORD=xyz ./encrypt.sh  # uses env var (CI/CD)
#
# Output: encrypted/slides.html (the file GitHub Pages serves)

set -euo pipefail

if [ ! -f slides.html ]; then
  echo "Error: slides.html not found. Render first with:"
  echo "  cd ../slide-creator && node render-direct.js gpu-deck-spec.json --notes=../gpu-as-a-service/SPEAKER_NOTES.md"
  exit 1
fi

npx staticrypt slides.html \
  --directory encrypted \
  --config false \
  --short \
  --remember 7 \
  --template-title "GPU as a Service — Red Hat OpenShift AI" \
  --template-instructions "Enter the presentation password to continue." \
  --template-color-primary "#EE0000" \
  --template-color-secondary "#151515"

echo ""
echo "Encrypted → encrypted/slides.html"
echo "Deploy the 'encrypted/' directory to GitHub Pages."
echo "DO NOT commit the password anywhere."
