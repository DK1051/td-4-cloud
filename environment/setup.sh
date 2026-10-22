#!/usr/bin/env bash
# Bicep CLI for local syntax checks; real deployments run in GitHub Actions via OIDC
if ! command -v bicep >/dev/null 2>&1; then
  curl -fsSL --max-time 120 -o /usr/local/bin/bicep "https://github.com/Azure/bicep/releases/latest/download/bicep-linux-x64" \
    && chmod +x /usr/local/bin/bicep || echo "WARN bicep download failed (CI still validates)"
fi
exit 0
