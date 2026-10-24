#!/usr/bin/env bash
# Bicep CLI for local syntax checks; real deployments run in GitHub Actions via OIDC
# Pinned to 0.48.1 (the version installed and recorded in docs/PROBES.md on 2026-10-22). Bump deliberately, in its own PR.
BICEP=0.48.1
# Where the download goes. Only changed when testing this script.
BICEP_BIN="${BICEP_BIN:-/usr/local/bin/bicep}"

# Which version is on PATH now? (empty when Bicep is missing)
have=""
if command -v bicep >/dev/null 2>&1; then
  have=$(bicep --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
fi

# Install when Bicep is missing OR is not the pinned version.
if [ "$have" != "$BICEP" ]; then
  echo "bicep: found '${have:-none}', want ${BICEP} - downloading"
  curl -fsSL --max-time 120 -o "${BICEP_BIN}.tmp" "https://github.com/Azure/bicep/releases/download/v${BICEP}/bicep-linux-x64" \
    && chmod +x "${BICEP_BIN}.tmp" && mv "${BICEP_BIN}.tmp" "${BICEP_BIN}" \
    || { rm -f "${BICEP_BIN}.tmp"; echo "WARN bicep download failed (CI still validates)"; }
fi
exit 0
