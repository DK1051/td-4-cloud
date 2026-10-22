#!/usr/bin/env bash
# Bicep CLI for local syntax checks; real deployments run in GitHub Actions via OIDC
# Pinned to 0.48.1 (the version installed and recorded in docs/PROBES.md on 2026-10-22). Bump deliberately, in its own PR.
BICEP=0.48.1
if ! command -v bicep >/dev/null 2>&1; then
  curl -fsSL --max-time 120 -o /usr/local/bin/bicep "https://github.com/Azure/bicep/releases/download/v${BICEP}/bicep-linux-x64" \
    && chmod +x /usr/local/bin/bicep || echo "WARN bicep download failed (CI still validates)"
fi
exit 0
