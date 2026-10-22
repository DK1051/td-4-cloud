"""Checks for the 4E Canada-Only Landing Zone files (T4-S01).

These tests only read files in this repository. Nothing here talks to Azure.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FOUR_E = REPO / "4e-canada-landing-zone"

# Folders that are never scanned (version control, virtual env, tool caches).
SKIP_DIRS = {".git", ".venv", ".pytest_cache", ".ruff_cache", "__pycache__"}

GUID_RE = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")
# The company name followed by a dot and a letter is a domain; only the
# fictional ".example" ending is allowed.
BAD_DOMAIN_RE = re.compile(r"mapleharbour\.(?!example(?![a-z]|\.[a-z]))[a-z]", re.IGNORECASE)

ROLE_ACTIONS = [
    "*/read",
    "Microsoft.Compute/virtualMachines/start/action",
    "Microsoft.Compute/virtualMachines/powerOff/action",
    "Microsoft.Compute/virtualMachines/deallocate/action",
]


def load(relative_path):
    return json.loads((FOUR_E / relative_path).read_text(encoding="utf-8"))


def repo_text_files():
    """Yield (path, text) for every readable text file in the repo, minus skipped folders."""
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if SKIP_DIRS.intersection(path.relative_to(REPO).parts):
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary file: nothing to scan


def test_all_json_files_parse():
    files = list(FOUR_E.rglob("*.json"))
    assert len(files) >= 3, "expected the two parameter files and the role file"
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))


def test_allowed_locations_are_exactly_canada():
    params = load("policies/allowed-locations.parameters.json")
    assert set(params) == {"listOfAllowedLocations"}
    values = params["listOfAllowedLocations"]["value"]
    assert set(values) == {"canadacentral", "canadaeast"}
    assert len(values) == 2


def test_tag_parameter_is_owner():
    params = load("policies/require-tags.parameters.json")
    assert params == {"tagName": {"value": "owner"}}


def test_role_actions_are_exactly_the_four_allowed():
    role = load("roles/portfolio-operator.json")
    assert role["Name"] == "Portfolio Operator (td-4)"
    assert role["IsCustom"] is True
    assert role["Actions"] == ROLE_ACTIONS
    assert role["NotActions"] == []
    assert role["DataActions"] == []
    assert role["NotDataActions"] == []


def test_role_scope_is_the_placeholder_only():
    role = load("roles/portfolio-operator.json")
    assert role["AssignableScopes"] == ["/subscriptions/<SUBSCRIPTION_ID>"]
    assert "portfolio-operator.local.json" in role["Description"]


def test_no_guid_shaped_string_anywhere_in_repo():
    hits = [str(p.relative_to(REPO)) for p, text in repo_text_files() if GUID_RE.search(text)]
    assert hits == [], f"GUID-shaped string found in: {hits}"


def test_only_the_example_domain_is_used():
    hits = [str(p.relative_to(REPO)) for p, text in repo_text_files() if BAD_DOMAIN_RE.search(text)]
    assert hits == [], f"domain other than mapleharbour.example in: {hits}"


def test_budget_and_alerts_guide_has_required_content():
    text = (FOUR_E / "BUDGET-AND-ALERTS.md").read_text(encoding="utf-8")
    for needle in ["50%", "80%", "100%", "Microsoft.Authorization/roleAssignments/write"]:
        assert needle in text, needle
    # The Tags-tab warning must come before Part A (and Part A must exist).
    assert "## Part A" in text
    assert "Tags" in text.split("## Part A")[0]


def test_signup_guide_has_all_six_rules():
    text = (FOUR_E / "SIGNUP.md").read_text(encoding="utf-8")
    for needle in ["new customers", "credit card", "30 days", "pay-as-you-go", "Track 3", "not earlier"]:
        assert needle in text, needle


def test_compliance_is_never_claimed():
    claim_denial = re.compile(r"NOT claim|claims no|does not claim", re.IGNORECASE)
    readme_lines = (FOUR_E / "README.md").read_text(encoding="utf-8").splitlines()
    # Not vacuous: the README must actually contain a denial line.
    assert any(re.search(r"complian", ln, re.IGNORECASE) and claim_denial.search(ln) for ln in readme_lines)
    for path in FOUR_E.rglob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if re.search(r"complian", line, re.IGNORECASE):
                assert claim_denial.search(line), f"{path.name}: {line}"


def test_diagram_has_one_mermaid_flowchart_block():
    text = (FOUR_E / "diagram.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)
    assert len(blocks) == 1
    assert blocks[0].lstrip().startswith("flowchart TB")
