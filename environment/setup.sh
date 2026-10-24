#!/usr/bin/env bash
# Bicep CLI for local syntax checks; real deployments run in GitHub Actions via OIDC
# Pinned to 0.48.1 (the version installed and recorded in docs/PROBES.md on 2026-10-22). Bump deliberately, in its own PR.
BICEP=0.48.1
# Where the download goes. Only changed when testing this script.
BICEP_BIN="${BICEP_BIN:-/usr/local/bin/bicep}"

# The version of the bicep found on PATH (empty when missing). A pre-release such as
# "0.48.1-preview" is kept whole, so it counts as a mismatch.
bicep_version() {
  command -v bicep >/dev/null 2>&1 || return 0
  bicep --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?' | head -1
}

have=$(bicep_version)

# Install when Bicep is missing OR is not the pinned version.
if [ "$have" != "$BICEP" ]; then
  echo "bicep: found '${have:-none}', want ${BICEP} - downloading"
  curl -fsSL --max-time 300 -o "${BICEP_BIN}.tmp" "https://github.com/Azure/bicep/releases/download/v${BICEP}/bicep-linux-x64" \
    && chmod +x "${BICEP_BIN}.tmp" && mv "${BICEP_BIN}.tmp" "${BICEP_BIN}" \
    || { rm -f "${BICEP_BIN}.tmp"; echo "WARN bicep download failed (CI still validates)"; }
  # Check again: an older bicep earlier on PATH would still win over the one just installed.
  now=$(bicep_version)
  [ "$now" = "$BICEP" ] || echo "WARN bicep on PATH is '${now:-none}', not ${BICEP} (an older copy earlier on PATH?)"
fi
exit 0
