# td-4-cloud — Track 4 · Cloud (Microsoft AZ-104)

Imagine someone phones a company's IT helpdesk, pretends to be an employee, and talks the agent into resetting that employee's password or their phone-based sign-in check. That is a real, current attack: in May 2026 the Canadian Centre for Cyber Security warned about it in alert [AL26-010](https://www.cyber.gc.ca/en/alerts-advisories/al26-010-cyber-criminals-social-engineering-enabled-compromise-enterprise-saas-environments). The other tracks of this portfolio try to stop the fake call, catch the stolen account, and make a fraudulent reset much less useful. This track is about what happens if everything else fails and the attacker is inside the company's cloud: The configuration for Microsoft Azure (the cloud platform covered by the AZ-104 certification) is written in this repo with AI assistance, but it has not yet been applied to Azure. It is designed so that the damage an attacker can do is small and visible. Once applied, the policies are meant to allow resources only in Canada (resources whose location is `global` are skipped) and to require an `owner` tag on resources (not on resource groups); deployments are meant to run without any stored password; and an AI assistant (framework built, evaluation cut, never run on an incident) is designed to draft the clean-up checklist for an incident without being allowed to run a command.

This is Track 4 of the [Takeover Defense](https://github.com/DK1051/takeover-defense) portfolio by Eojin Kim. Everything here uses a fictional company, **Maple Harbour Credit Union** (`mapleharbour.example`). No real people, accounts or identifiers appear in this repository.

## Status

| Project | Level | Status |
|---|---|---|
| 4E Canada-Only Landing Zone | Easy | Built (T4-S01; not yet applied to Azure) |
| 4H Secretless Deploy | Hard | Built (T4-S02; Azure runs pending) |
| 4A Containment Runbook Copilot | Hard + AI | Cut (framework + scorer built; evaluation moved past Nov 5) |

Status values (the same words as the hub): Planned → In progress → Built → Verified → Cut (moved to after Nov 5). "Built" means Claude's part is done and checked by the verifier; I have not yet run anything against Azure.

## Projects

### 4E Canada-Only Landing Zone — `4e-canada-landing-zone/`
A "landing zone" is the set of guard-rails you put on a cloud account before you build anything in it. Once applied, this one is meant to keep resources inside Canada (Azure regions `canadacentral` and `canadaeast`; resources whose location is `global` are skipped) and to require an `owner` tag on resources (not on resource groups); it defines a limited "operator" role that can read everything but only start and stop virtual machines, and gives the portal steps for a spending budget plus an alert that fires whenever someone is given new permissions (neither is set up yet). It mirrors the intent of the Government of Canada's data-residency direction for sensitive data; it does not claim compliance with anything.

### 4H Secretless Deploy — `4h-secretless-deploy/`
A GitHub Actions workflow, written but not yet run, that is meant to deploy an Azure storage account with four settings locked (HTTPS only, TLS 1.2+, no public blobs, no account keys; network access is not restricted) from a Bicep template (Bicep is Azure's language for describing resources as code) using OpenID Connect (OIDC). OIDC lets GitHub prove to Azure "this is workflow X in repository Y" with a short-lived signed token, so no password, key or certificate is stored (three identifiers are kept as GitHub secrets). A second workflow, not yet run against Azure, is written to try three things the deployment identity must NOT be able to do, and to pass only if Azure refuses each one.

### 4A Containment Runbook Copilot — `4a-containment-copilot/`
An AI assistant that reads an incident summary (from my own Track 2 investigations) and drafts a containment checklist: revoke sessions, remove the newly added sign-in method, remove new permissions, block sign-in, preserve evidence — and never touch the emergency "break-glass" accounts. Every command is written as a commented-out dry run; the assistant has no ability to execute anything. Its plans will be scored against answer keys I write from Microsoft Learn, for three models; the framework and scorer are built, and the evaluation runs after my CompTIA A+ exam.

## How this repo is built

- Work happens in short, planned sessions. Each session has a brief in `docs/briefs/` and a line in `docs/RUN-SHEET.md`.
- Claude Code does the building: a director model plans, a builder writes code, a verifier checks the result against the brief and writes `docs/verify/<ID>.md`, and a separate reviewer model red-teams designs before anything AI-driven is built. `AI-USE.md` records what Claude did and what I did, per project. `COSTS.md` records what each session cost.
- Class sessions (`docs/learning/`) are where I explain the code back and answer "why" questions without hints. If I cannot explain a file in this repo, it does not stay.
- Surprises and plan changes are logged in `docs/CAVEATS.md` rather than hidden.

## How to verify my work

- `docs/verify/` — the verifier's pass/fail report for every session, with evidence.
- `docs/learning/` — class transcripts.
- The commit history and pull requests, one per session.
- `.github/workflows/ci.yml` — lint, tests, a secret scan and a Bicep build on every pull request and every merge to `main`.

## Safety rules

No Azure credentials, tenant IDs or subscription IDs ever enter a Claude session or this repository. Deployments and the cannot-do tests run only in GitHub Actions through OIDC, with the three identifiers held as GitHub Actions secrets that I set myself. All companies, people, phone numbers and e-mail addresses in the data are fictional. Everything here is defensive.

## Running the checks locally

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
ruff check .
pytest -q
```
