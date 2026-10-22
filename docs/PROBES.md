# Probes — td-4-cloud

### 2026-10-22 (T4-S01)

## Probe 2026-10-22T09:58Z
- arch: x86_64
- cpus: 4  memory: 15 GB
- avx2 flags: 4
- python: Python 3.13.16
- java: Picked up JAVA_TOOL_OPTIONS: [proxy settings removed before commit — they list internal proxy hosts]
- docker:   not available
- pwsh: 7.6.7
- keycloak: /opt/keycloak Keycloak 26.8.1
- reach https://repo1.maven.org/maven2/ -> HTTP 429
- reach https://mcr.microsoft.com/v2/ -> HTTP 200
- reach https://packages.microsoft.com/ -> HTTP 200
- reach https://pypi.org/simple/ -> HTTP 200
- reach https://www.powershellgallery.com/ -> HTTP 000
- reach https://graph.microsoft.com/v1.0/ -> HTTP 000
- reach https://management.azure.com/ -> HTTP 000
- bicep: Bicep CLI version 0.48.1 (cec7951cf6)

Notes on this run (added by the director, not by `probe.sh`): the `java:` line's proxy host list was removed before commit (it names internal hosts); `docker:` and `keycloak:` each printed over two lines and are joined here. This probe ran in one cloud session shared with the hub and the other three tracks (Eojin's D0 launch), on the same machine where the Track 1, 3 and 4 setup scripts had just run.

What this means for Track 4:
- `bicep: 0.48.1` — the Bicep tool (which turns Azure infrastructure files into deployable templates) is installed, so T4-S02 can check Bicep files locally as well as in CI. The setup script downloads the "latest" release rather than a pinned version, so the version may differ between environments (caveat logged).
- `management.azure.com -> HTTP 000` — Azure's management API is blocked here, as intended: no file in this session is tested against Azure; Eojin applies them in Azure Cloud Shell.
- `reach https://github.com/` is not part of `probe.sh`; GitHub's API is used in this session only to read Microsoft's public policy repository.
