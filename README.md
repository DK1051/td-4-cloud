# td-4-cloud — Track 4 · Cloud (Microsoft AZ-104)

Imagine someone phones a company's IT helpdesk, pretends to be an employee, and talks the agent into resetting that employee's password or their phone-based sign-in check. That is a real, current attack: in May 2026 the Canadian Centre for Cyber Security warned about it in alert [AL26-010](https://www.cyber.gc.ca/en/alerts-advisories/al26-010-cyber-criminals-social-engineering-enabled-compromise-enterprise-saas-environments). The other tracks of this portfolio try to stop the fake call, catch the stolen account, and make the reset worthless. This track is about what happens if everything else fails and the attacker is inside the company's cloud: I set up Microsoft Azure (the cloud platform covered by the AZ-104 certification) so that the damage they can do is small, visible and reversible. Resources can only be created in Canada, every resource must name an owner, deployments run without any stored password, and an AI assistant drafts the clean-up checklist for an incident without ever being allowed to run a command.

This is Track 4 of the [Takeover Defense](https://github.com/DK1051/takeover-defense) portfolio by Eojin Kim. Everything here uses a fictional company, **Maple Harbour Credit Union** (`mapleharbour.example`). No real people, accounts or identifiers appear in this repository.

## Status

| Project | Level | Status |
|---|---|---|
| 4E Canada-Only Landing Zone | Easy | Planned |
| 4H Secretless Deploy | Hard | Planned |
| 4A Containment Runbook Copilot | Hard + AI | Planned |

Status values: Planned → In progress → Built (Claude's work verified) → Applied (I ran it against my own Azure account) → Reviewed (class session done).

## Projects

### 4E Canada-Only Landing Zone — `4e-canada-landing-zone/`
A "landing zone" is the set of guard-rails you put on a cloud account before you build anything in it. This one keeps every resource inside Canada (Azure regions `canadacentral` and `canadaeast`), requires an `owner` tag on everything, defines a limited "operator" role that can read everything but only start and stop virtual machines, and sets up a spending budget plus an alert that fires whenever someone is given new permissions. It mirrors the intent of the Government of Canada's data-residency direction for sensitive data; it does not claim compliance with anything.

### 4H Secretless Deploy — `4h-secretless-deploy/`
A GitHub Actions workflow that deploys a locked-down Azure storage account from a Bicep template (Bicep is Azure's language for describing resources as code) using OpenID Connect (OIDC). OIDC lets GitHub prove to Azure "this is workflow X in repository Y" with a short-lived signed token, so no password or key is ever stored. A second workflow tries three things the deployment identity must NOT be able to do, and passes only if Azure refuses each one.

### 4A Containment Runbook Copilot — `4a-containment-copilot/`
An AI assistant that reads an incident summary (from my own Track 2 investigations) and drafts a containment checklist: revoke sessions, remove the newly added sign-in method, remove new permissions, block sign-in, preserve evidence — and never touch the emergency "break-glass" accounts. Every command is written as a commented-out dry run; the assistant has no ability to execute anything. I grade its plans against answer keys I wrote from Microsoft Learn, and compare three models.

## How this repo is built

- Work happens in short, planned sessions. Each session has a brief in `docs/briefs/` and a line in `docs/RUN-SHEET.md`.
- Claude Code does the building: a director model plans, a builder writes code, a verifier checks the result against the brief and writes `docs/verify/<ID>.md`, and a separate reviewer model red-teams designs before anything AI-driven is built. `AI-USE.md` records what Claude did and what I did, per project. `COSTS.md` records what each session cost.
- Class sessions (`docs/learning/`) are where I explain the code back and answer "why" questions without hints. If I cannot explain a file in this repo, it does not stay.
- Surprises and plan changes are logged in `docs/CAVEATS.md` rather than hidden.

## How to verify my work

- `docs/verify/` — the verifier's pass/fail report for every session, with evidence.
- `docs/learning/` — class transcripts.
- The commit history and pull requests, one per session.
- `.github/workflows/ci.yml` — lint, tests, a secret scan and (once 4H exists) a Bicep build on every pull request and every merge to `main`.

## Safety rules

No Azure credentials, tenant IDs or subscription IDs ever enter a Claude session or this repository. Deployments and the cannot-do tests run only in GitHub Actions through OIDC, with the three identifiers held as GitHub Actions secrets that I set myself. All companies, people, phone numbers and e-mail addresses in the data are fictional. Everything here is defensive.

## Running the checks locally

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
ruff check .
pytest -q
```
