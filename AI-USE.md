# What Claude did vs what Eojin did

Filled in at the `wrap` step of every session. "Claude" lists the model that did each piece of work (director Opus 5.5, builder Sonnet 5.5, chores Haiku 5.5, verifier Opus 5.5, redteam Fable 5.1). "Eojin" lists what I did myself: decisions, inputs, manual steps in Azure and GitHub, grading.

## 4E Canada-Only Landing Zone

Claude (models used)
- T4-S01 director (Opus 5.5): probe and `bicep --version`, caveats, run sheet, PR.
- T4-S01 `builder` (Sonnet 5.5): confirmed the three built-in policy names and parameters from Microsoft's public azure-policy files, wrote the parameter files, the custom role, `BUDGET-AND-ALERTS.md`, `SIGNUP.md`, the 4E README, `diagram.md` and 11 tests. Nothing touched Azure.
- T4-S01 `redteam` (Fable 5.1): mid-review. `verifier` (Opus 5.5): final check, `docs/verify/T4-S01.md`.

Eojin
- To do: on the day you configure 4E, follow `SIGNUP.md`, then apply the files in Azure Cloud Shell in the README's order, set up the budget and alert in the portal, and fill the Results table.

## 4H Secretless Deploy

Claude (models used)
- T4-S02 director (Opus 5.5): planned, closed the Bicep-pinning gap with the builder, checked the guide's URLs, asked Eojin the design choices, logged caveats, opened the PR.
- T4-S02 `builder` (Sonnet 5.5): `main.bicep`, the `deploy.yml` and `cannot-do.yml` workflows with `verdict.sh`, the Bicep pin in CI and `setup.sh`, `OIDC-SETUP.md`, the 4H README, and 36 tests.
- T4-S02 `redteam` (Fable 5.1): mid-review (8 items + 2 design choices), all handled. `verifier` (Opus 5.5): final check, `docs/verify/T4-S02.md`.

Eojin
- Decided: cannot-do (c) accepts only AuthorizationFailed; the storage account has no usable keys (sign-in only). Still to do: follow `OIDC-SETUP.md` (check the subject format on GitHub's page first), set the three secrets, run "4H deploy" then "4H cannot-do", paste the run links into the Results table, record the credit balance.

## 4A Containment Runbook Copilot

Claude (models used)
- (to be filled at wrap)

Eojin
- (to be filled at wrap)
