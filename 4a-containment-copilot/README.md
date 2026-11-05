# 4A Containment Runbook Copilot

## Status
**Cut: framework and scorer complete; the real evaluation has not been run.** The evaluation needs my incident reports and answer keys, which come from my 2E blind hunt (Track 2). It is scheduled after my CompTIA A+ exam, run on my Claude plan usage. Until then `incidents/`, `answer-keys/`, `runs/` and `RESULTS.md` do not exist, and there are no results to show.

## What it does
When an attacker takes over an employee's account, the first job is **containment**: stop them doing more damage before anyone cleans up or investigates in depth. This project is an AI assistant (the "copilot") that reads one of my incident reports about a Microsoft Entra ID account takeover at the fictional Maple Harbour Credit Union (`mapleharbour.example`) and drafts a containment checklist for a trained person to review:

1. preserve evidence (export sign-in and audit logs) before changing anything,
2. revoke the user's sign-in sessions,
3. remove the sign-in (MFA) method the attacker added,
4. remove the role assignment (permission) the attacker added,
5. block sign-in to the account.

It must never touch the **break-glass accounts** — emergency admin accounts kept aside for when normal sign-in is broken; changing them during an incident could lock everyone out. Every command it writes is a **dry run**: a line starting with `# DRY RUN:`, which is a comment, so it is text for a person to read and nothing runs it. When it is not sure of a command's exact name it must write `TODO(verify)` instead of guessing, and "not in the report" instead of inventing details.

A scorer then compares each plan with my answer key and counts correct, missing and harmful steps for three Claude models (Haiku, Sonnet, Opus).

## Files
| File | What it is |
|---|---|
| `DESIGN.md` | One-page design: inputs, the copilot's rules, the scoring method, what is not measured. |
| `DESIGN-REVIEW.md` | The `redteam` review of the design before any code, and each change made because of it. |
| `../.claude/agents/containment-bot.md` | The copilot itself: a Claude Code sub-agent that can only `Read` and `Glob` (list) files. It has no tool that can run a command, write a file or reach the network. |
| `scripts/make_batch.py` | Writes `runs/batch-prompt.md`: the instruction plus the list of incident files. |
| `scripts/split_run.py <model>` | Splits one model's answer (`runs/<model>/raw.md`) into one file per incident, fails loudly if a block is broken or if an incident in `incidents/` has no block, and replaces anything shaped like an Azure ID with `<guid-redacted>`. |
| `scripts/score.py` | Scores every plan against its answer key and writes `RESULTS.md`. |
| `../tests/test_4a_score.py` | Tests for the scorer and splitter, with fixture plans in `../tests/fixtures/4a/` (written by Claude as test data; they are not my answer keys). |

## How to run it (once the incidents and keys exist)
From the repo root, with the virtual environment active:
1. `python 4a-containment-copilot/scripts/make_batch.py`
2. Move `4a-containment-copilot/answer-keys/` out of the repo (for example to `/tmp`) so the copilot cannot read the answers.
3. For each model, one after another (so each credit difference belongs to one model): read the credit balance, run the `containment-bot` sub-agent ONCE with the batch prompt and the Agent tool's `model` set to `haiku`, then `sonnet`, then `opus`; save its answer to `runs/<model>/raw.md`; read the balance again and write the difference to `runs/<model>/cost.txt`; run `python 4a-containment-copilot/scripts/split_run.py <model>`. One model, one call for all incidents, no re-runs (a poor plan is a result). Only if a model refuses or the split fails is one retry allowed, and it is logged.
4. Put `answer-keys/` back, then `python 4a-containment-copilot/scripts/score.py`.

## Who did what
- **Me (Eojin):** approved the scoped framework-only run. Still to do: the incident reports and answer keys (from my 2E hunt and Microsoft Learn), the three model runs and credit readings, and the manual grade in class session T4-C2.
- **Claude:** the director (Opus) wrote `DESIGN.md` and this README; `redteam` (Fable) reviewed the design; `builder` (Sonnet) wrote the copilot prompt, the three scripts and the tests; `verifier` (Opus) checked them. Details in `../AI-USE.md`.

## Results
None yet — the evaluation has not run. The table from `RESULTS.md` will be copied here, with the date, after it does.

## Limits (read these before trusting any number)
- **The keyword scorer is wrong in both directions sometimes.** It can mark a correct plan "missing" when the plan uses a different command than my key lists, and mark a wrong plan "present" when the right word appears in the wrong place. My manual grade in T4-C2 is the real result.
- **Never run these plans against a real tenant.** They are drafts for a trained person to check. Nothing in this repository runs them, and the copilot never had a tool that could execute anything — but a person could still copy a line, so treat every plan as unchecked.
- **The checklist order above has a known gap.** It blocks sign-in last (step 5), so an attacker who still knows the reset password could sign back in during steps 2 to 4, and it has no password-reset step after the MFA cleanup. The scorer would still rate such a plan complete. The order has not been fixed yet.
- "No harmful or live commands" only ever means "the keyword check found none".
- The copilot's closing line ("Never-touch list checked…") is its own claim; the scorer ignores it.
- With 3–5 incidents and one run per model, the results are counts, not a ranking of models.
- My answer keys are unchecked until T4-C2.
- The incident reports come from a synthetic (made-up) dataset, so some details (exact role names, device IDs) may be missing; "not in the report" is the correct answer then.
