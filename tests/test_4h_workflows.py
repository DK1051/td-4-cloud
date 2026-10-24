"""Checks for the 4H Secretless Deploy files (T4-S02).

These tests only read files in this repository. Nothing here talks to Azure or GitHub.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO / ".github" / "workflows"
FOUR_H = REPO / "4h-secretless-deploy"

DEPLOY_WORKFLOWS = ["deploy.yml", "cannot-do.yml"]
ALLOWED_SECRETS = {"AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID", "GITHUB_TOKEN"}


def load_workflow(name):
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def triggers(wf):
    # PyYAML reads the key `on:` as the boolean True, so look for both spellings.
    # If neither is present this raises, so the tests cannot silently test nothing.
    if "on" in wf:
        return wf["on"]
    return wf[True]


def all_steps(wf):
    return [step for job in wf["jobs"].values() for step in job["steps"]]


@pytest.mark.parametrize("name", DEPLOY_WORKFLOWS)
def test_trigger_is_workflow_dispatch_only(name):
    trig = triggers(load_workflow(name))
    assert set(trig) == {"workflow_dispatch"}


@pytest.mark.parametrize("name", DEPLOY_WORKFLOWS)
def test_permissions_are_exactly_id_token_and_contents_read(name):
    assert load_workflow(name)["permissions"] == {"id-token": "write", "contents": "read"}


@pytest.mark.parametrize("name", DEPLOY_WORKFLOWS)
def test_exactly_one_azure_login_with_the_three_secrets(name):
    logins = [s for s in all_steps(load_workflow(name)) if s.get("uses") == "azure/login@v3"]
    assert len(logins) == 1
    assert logins[0]["with"] == {
        "client-id": "${{ secrets.AZURE_CLIENT_ID }}",
        "tenant-id": "${{ secrets.AZURE_TENANT_ID }}",
        "subscription-id": "${{ secrets.AZURE_SUBSCRIPTION_ID }}",
    }


@pytest.mark.parametrize("name", DEPLOY_WORKFLOWS)
def test_only_the_three_azure_secrets_are_referenced(name):
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    used = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", text))
    assert used == {"AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID"}


def test_every_secret_in_every_workflow_is_on_the_allowed_list():
    for path in WORKFLOWS.glob("*.yml"):
        used = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", path.read_text(encoding="utf-8")))
        assert used <= ALLOWED_SECRETS, f"{path.name}: {used - ALLOWED_SECRETS}"


def test_ci_still_has_a_single_job_called_checks():
    assert list(load_workflow("ci.yml")["jobs"]) == ["checks"]


def test_ci_and_setup_script_pin_bicep_0_48_1():
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "az bicep install --version v0.48.1" in ci
    assert ci.index("az bicep install") < ci.index("az bicep build")
    setup = (REPO / "environment" / "setup.sh").read_text(encoding="utf-8")
    assert "BICEP=0.48.1" in setup
    assert setup.rstrip().endswith("exit 0")


def test_bicep_template_is_locked_down():
    text = (FOUR_H / "main.bicep").read_text(encoding="utf-8")
    for needle in [
        "supportsHttpsTrafficOnly: true",
        "minimumTlsVersion: 'TLS1_2'",
        "allowBlobPublicAccess: false",
        "location string = 'canadacentral'",
        "Standard_LRS",
        "StorageV2",
        "owner: owner",
    ]:
        assert needle in text, needle


def test_bicep_outputs_only_the_account_name():
    text = (FOUR_H / "main.bicep").read_text(encoding="utf-8")
    outputs = re.findall(r"^output\s+(\w+)\s+\w+\s*=\s*(.+)$", text, re.MULTILINE)
    assert outputs == [("storageAccountName", "storage.name")]


def test_bicep_account_name_prefix_fits_the_24_character_limit():
    text = (FOUR_H / "main.bicep").read_text(encoding="utf-8")
    match = re.search(r"var storageAccountName = '([a-z0-9]+)\$\{uniqueString\(resourceGroup\(\)\.id\)\}'", text)
    assert match, "name must be a short prefix plus uniqueString(resourceGroup().id)"
    assert 3 <= len(match.group(1)) + 13 <= 24  # uniqueString returns 13 characters


def test_cannot_do_has_three_steps_that_pass_only_on_the_specific_codes():
    wf = load_workflow("cannot-do.yml")
    scripts = [s["run"] for s in all_steps(wf) if "run" in s]
    assert len(scripts) == 3
    a, b, c = scripts
    assert "RequestDisallowedByPolicy" in a and "location=westus" in a
    assert "AuthorizationFailed" in b and "--role Reader" in b and "::add-mask::$OID" in b
    assert "AuthorizationFailed" in c and "ResourceGroupNotFound" in c
    for script in scripts:
        assert "set +e" in script and "set -e" in script
        assert "FAIL: failed for another reason" in script
        assert "grep -q" in script  # pass only when the specific code is found
        assert "grep -o '([A-Za-z]*)'" in script  # failures print codes only
        assert "--output none" in script


def test_cannot_do_never_prints_the_captured_error_text():
    wf = load_workflow("cannot-do.yml")
    for step in all_steps(wf):
        for line in step.get("run", "").splitlines():
            if re.search(r'\$out\b|\$\{out\}', line) and re.search(r"\b(echo|printf)\b", line):
                # allowed only when the text goes into grep (a code check), never to the log
                assert "| grep" in line, line
