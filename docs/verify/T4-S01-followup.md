# Verify: T4-S01 follow-up (pin Bicep 0.48.1)

Date: 2026-10-22. Verifier: Claude (Opus 5.5). Branch `claude/friendly-heisenberg-seafff`, PR #2.
Compared against `origin/main` (a4bfc69, which already contains the merged T4-S01 PR). The local `main` (127430b) is stale, so it was also run as a second baseline.

## Review findings

The diff is 2 files: `environment/setup.sh` (+3/-1) and `docs/CAVEATS.md` (+1).

- `bash -n environment/setup.sh`: rc=0.
- The pinned URL `https://github.com/Azure/bicep/releases/download/v0.48.1/bicep-linux-x64` returns `200` from `curl -sIL`. 0.48.1 matches the version recorded in `docs/PROBES.md:21`.
- The `curl -f … && chmod … || echo WARN` and `exit 0` behaviour is unchanged, so a failed download still does not break environment setup.
- No other tracked file points the setup at `releases/latest`. `git grep "releases/latest|latest/download"` only hits `docs/CAVEATS.md:8`, which is a dated record and excluded. The only other "latest" is `runs-on: ubuntu-latest` in CI, which is not related.
- No mid-review was required for this follow-up.
- Notes (not defects, no fix required in this PR):
  1. `if ! command -v bicep` skips the download whenever any bicep is already on PATH, so an environment that already has a different version is not corrected. Running `bicep --version` again after the re-paste would confirm 0.48.1.
  2. CI's "Bicep build" step uses `az bicep build`, which installs whatever Bicep version `az` picks. That is not pinned to 0.48.1. It is out of this PR's scope ("setup"), but it may matter in T4-S02. One possible fix is `az bicep install --version v0.48.1` before the build. TODO(verify) that flag in the az docs first.
  3. As CAVEATS line 14 says, the cloud environment's Setup-script field keeps its own copy, so Eojin has to re-paste it.

## Regression

| Check | local main (127430b) | origin/main (a4bfc69) | branch (2d14531) |
|---|---|---|---|
| `ruff check .` | All checks passed! | All checks passed! | All checks passed! |
| `pytest -q` (repo .venv) | no tests ran (rc 5) | 11 passed | 11 passed |

Nothing that passed on main fails now. The temporary worktree `/tmp/t4f-main` was created and then removed. Secrets and real-data grep of the added lines: the only hit is the public GitHub release URL, a false positive. There are no keys, tokens, IDs or real emails.

## Criteria

- Bicep pinned to 0.48.1 in `environment/setup.sh`: PASS. `BICEP=0.48.1` is set, the URL uses `download/v${BICEP}/`, and the URL check gives HTTP `200`.
- No remaining `releases/latest` in the setup path: PASS (only the dated CAVEATS record).
- ruff and pytest on branch vs main: PASS ("11 passed" on both).

Verdict: PASS. New caveat: the CI `az bicep build` step is still unpinned (note 2). Suggest a CAVEATS line for T4-S02.
