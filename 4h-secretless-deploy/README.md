# 4H Secretless Deploy

## What it does
This project deploys a locked-down Azure storage account from GitHub **without any stored password or key**, and then proves what the deploying identity is NOT allowed to do. It belongs to the fictional Maple Harbour Credit Union (`mapleharbour.example`).

Plain-English glossary:
- **Bicep** is Azure's language for describing resources as code. `main.bicep` describes one storage account: Canada by default, HTTPS only, TLS 1.2 or newer, no public access to blobs (files in storage), an `owner` tag, and an output of the account name only.
- **OIDC (OpenID Connect)** lets GitHub give Azure a short-lived signed token that says "this is workflow X in repository Y on branch main". Nothing secret is stored in GitHub or in this repository.
- A **federated credential** is the rule you register in Azure that says which exact repository and branch may use that token to log in. `OIDC-SETUP.md` explains how to create it, including the one subject-string detail that breaks everything if it is wrong.
- A **workflow** is a GitHub Actions script. `workflow_dispatch` means it starts only when I press **Run workflow** by hand; there is no automatic trigger.

## How to run it
1. Do the one-time setup in `OIDC-SETUP.md` (and apply the 4E policies first, see `../4e-canada-landing-zone/README.md`).
2. GitHub, **Actions** tab, **4H deploy**, **Run workflow** on `main`. PASS looks like a log ending in `Succeeded`.
3. Then **4H cannot-do**, **Run workflow** on `main`. PASS looks like three lines starting `PASS:` and a green job. Any line starting `FAIL:` turns the job red.

## What each cannot-do test proves
| Check | Expected refusal | Proves | Depends on |
|---|---|---|---|
| (a) Deploy `main.bicep` with `location=westus` | `RequestDisallowedByPolicy` | The Canada-only rule stops even a legitimate deployer from creating resources elsewhere. | The 4E "Allowed locations" policy is assigned and already in force. |
| (b) Create a Reader role assignment for the deploy identity itself | `AuthorizationFailed` | If the identity were stolen, it could not give itself or anyone else more power. | The identity has Contributor, which cannot write role assignments. |
| (c) Read the resource group `rg-td4-private` | `AuthorizationFailed` or `ResourceGroupNotFound` | The identity can only see the one resource group it was given. | Contributor is assigned on `rg-td4-canada` only, nothing on `rg-td4-private`. |

Each check passes only when the output contains the specific code. If the command unexpectedly succeeds, or fails for any other reason, the job fails and prints only error codes (never the full error text, which can contain IDs).

## What Eojin did / what Claude did
| Who | What |
|---|---|
| Claude | Wrote `main.bicep`, both workflows, the tests and the guides, and checked that the Bicep compiles and the workflow shell logic behaves against a stand-in `az` command. Claude never connected to Azure and never saw an ID. |
| Eojin | Follows `OIDC-SETUP.md`, sets the three GitHub secrets, runs both workflows, and fills in the Results table. Not done yet; this project stays "Built" until he has. |

## Results
Fill in after running. Links are public and safe to paste; raw output is not.

| Workflow | Date | Run link | Outcome |
|---|---|---|---|
| 4H deploy | | | |
| 4H cannot-do | | | |

## Limits
- One resource group, one branch (`main`): the federated credential pins `main`, so a run from any other branch fails to log in by design.
- Public logs: GitHub masks only the three secrets, so the workflows print error codes only, and raw output never goes in this README.
- A new policy assignment takes time to start enforcing; the documented delay is `TODO(verify)`. Check (a) proves something only once the 4E policies are in force.
- The Bicep API version `2026-06-01` is the newest one the compiler (Bicep 0.48.1) accepts without a warning. If the first deploy rejects it in `canadacentral`, fall back to `2025-06-01` in `main.bicep`.
- Not tested against Azure from the cloud session; the real test is Eojin's run.
- The storage account costs a little. Delete the resource group `rg-td4-canada` when done, or keep it for demos: Eojin's call.

## URL check (2026-10-24, from the cloud session)

| URL in `OIDC-SETUP.md` | Result |
|---|---|
| https://api.github.com/repos/DK1051/td-4-cloud | reachable (HTTP 200) |
| https://docs.github.com/en/actions/reference/security/oidc | unchecked (blocked from this network) |
| https://token.actions.githubusercontent.com | unchecked (blocked from this network); it is the token issuer, typed into Azure, not a page to open |
