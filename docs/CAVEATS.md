# Caveats found during execution

One line per surprise, appended during sessions (see CLAUDE.md, "Live adaptation"):

`- YYYY-MM-DD <ID> | what happened | impact: this session / <later IDs> / plan | what I did | needs Eojin: yes/no`
- 2026-10-22 T4-S01 | Ran in one cloud session with the hub and the other tracks (Eojin's D0 launch, no plan-approval stop); this session can push only to `claude/friendly-heisenberg-seafff`, not the brief's branch name | impact: this session | used that branch; one PR | needs Eojin: no
- 2026-10-22 T4-S01 | Credit balances not available during the unattended run; the usage menu shows one combined number for all five D0 sessions | impact: this session | placeholders in `COSTS.md`; record the combined number in the hub `COSTS.md` | needs Eojin: yes
- 2026-10-22 T4-S01 | `environment/setup.sh` downloads Bicep from `releases/latest`, not a pinned version (CLAUDE.md says pin versions); 0.48.1 was installed today | impact: T4-S02 (version may drift between environments) | recorded the version in `docs/PROBES.md`; script not changed in this session | needs Eojin: yes (decide whether to pin it to 0.48.1)
- 2026-10-22 T4-S01 | Brief's Day is D1; it ran on D0 at Eojin's request. Needs said "kit merged to main" — the kit is on `main` (commit 127430b) | impact: plan | none | needs Eojin: no
- 2026-10-22 T4-S01 | api.github.com returned HTTP 403 here, so the builder could not list the Azure/azure-policy folders; it fetched the files directly from raw.githubusercontent.com (HTTP 200) and accepted each name only when the file's displayName matched | impact: this session | source URLs recorded in the 4E README | needs Eojin: no
- 2026-10-22 T4-S01 | The Government of Canada data-residency direction URL ("from the spec") is not in any repo, so the 4E README has TODO(verify) instead of a URL | impact: this session | not guessed | needs Eojin: yes (paste the URL from the spec)
- 2026-10-22 T4-S01 | Redteam mid-review: must-fix — the alert rule and action group need a resource group and none existed, so the portal would create one outside Canada and our own policy would deny it; plus 12 cheaper items (lookup guards, no ID-bearing output, softer free-account claims, dropped an out-of-brief step) | impact: this session | builder applied them | needs Eojin: no
