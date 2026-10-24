"""Checks for the 4H Secretless Deploy files (T4-S02).

These tests only read files in this repository. Nothing here talks to Azure or GitHub.
"""

import re
import subprocess
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
    # az would otherwise use any Bicep found on the runner's PATH, which makes the pin ineffective.
    assert "az config set bicep.use_binary_from_path=false" in ci
    assert ci.index("use_binary_from_path=false") < ci.index("az bicep install")
    assert "az bicep version | grep -q '0\\.48\\.1' || { echo \"FAIL: wrong Bicep version\"; exit 1; }" in ci
    assert ci.index("grep -q '0\\.48\\.1'") < ci.index("az bicep build")
    setup = (REPO / "environment" / "setup.sh").read_text(encoding="utf-8")
    assert "BICEP=0.48.1" in setup
    assert setup.rstrip().endswith("exit 0")
    assert "--max-time 300" in setup
    assert "(-[0-9A-Za-z.]+)?" in setup  # a pre-release suffix counts as a different version
    assert "WARN bicep on PATH" in setup


def test_bicep_template_is_locked_down():
    text = (FOUR_H / "main.bicep").read_text(encoding="utf-8")
    for needle in [
        "supportsHttpsTrafficOnly: true",
        "minimumTlsVersion: 'TLS1_2'",
        "allowBlobPublicAccess: false",
        "allowSharedKeyAccess: false",
        "defaultToOAuthAuthentication: true",
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


VERDICT_SH = FOUR_H / "verdict.sh"
SOURCE_LINE = '. "$GITHUB_WORKSPACE/4h-secretless-deploy/verdict.sh"'


def cannot_do_scripts():
    return [s["run"] for s in all_steps(load_workflow("cannot-do.yml")) if "run" in s]


def test_cannot_do_has_three_steps_that_pass_only_on_the_specific_codes():
    scripts = cannot_do_scripts()
    assert len(scripts) == 3
    a, b, c = scripts
    assert "RequestDisallowedByPolicy" in a and "location=westus" in a
    assert "REQUIRE_ALSO=allowed-locations" in a  # must be refused by OUR location rule
    assert "AuthorizationFailed" in b and "--role Reader" in b and "::add-mask::$OID" in b
    # (c) accepts AuthorizationFailed only (Eojin's decision); "not found" is a failure.
    assert "group missing or identity can read the subscription" in c
    verdict_calls = [ln for ln in c.splitlines() if ln.strip().startswith("verdict ")]
    assert len(verdict_calls) == 1 and verdict_calls[0].rstrip().endswith("AuthorizationFailed")
    for script in scripts:
        assert SOURCE_LINE in script
        assert "set +e" in script and "set -e" in script
        assert "--output none" in script


def test_verdict_script_passes_only_on_codes_and_prints_codes_only():
    text = VERDICT_SH.read_text(encoding="utf-8")
    assert "grep -q" in text  # pass only when the specific code is found
    assert "FAIL: failed for another reason" in text
    assert "grep -oE" in text and "Code: *[A-Za-z]+" in text  # nested codes are found
    for line in text.splitlines():
        if re.search(r"\$\{?out\b", line) and re.search(r"\b(echo|printf)\b", line):
            raise AssertionError(f"verdict.sh prints the captured text: {line}")


def test_workflows_never_print_the_captured_error_text_or_trace_commands():
    for name in DEPLOY_WORKFLOWS:
        for step in all_steps(load_workflow(name)):
            run = step.get("run", "")
            assert "set -x" not in run and "set -o xtrace" not in run, name
            for line in run.splitlines():
                if re.search(r"\$out\b|\$\{out\}", line) and re.search(r"\b(echo|printf)\b", line):
                    raise AssertionError(f"{name} prints the captured text: {line}")
    assert "set -x" not in VERDICT_SH.read_text(encoding="utf-8")


def test_deploy_workflow_succeeds_only_on_the_word_succeeded():
    run = next(s["run"] for s in all_steps(load_workflow("deploy.yml")) if "run" in s)
    assert "grep -qx Succeeded" in run
    assert "Code: *[A-Za-z]+" in run  # failures print codes only


SECRET_TEXT = "SECRET-MESSAGE object id 12345"


def run_verdict(fake_command, *wanted, require_also=None):
    """Run verdict.sh the way the workflow does (bash -e with pipefail) against a fake command."""
    script = (
        '. "$VERDICT"; set +e; out=$(bash -c "$FAKE" 2>&1); code=$?; set -e; '
        'verdict "the thing should have been denied" "$code" "$out" ' + " ".join(wanted)
    )
    env = {"PATH": "/usr/bin:/bin", "VERDICT": str(VERDICT_SH), "FAKE": fake_command}
    if require_also:
        env["REQUIRE_ALSO"] = require_also
    return subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script], check=False, env=env, capture_output=True, text=True
    )


def test_verdict_fails_when_the_command_succeeds():
    r = run_verdict(f"echo {SECRET_TEXT}; exit 0", "AuthorizationFailed")
    assert r.returncode == 1
    assert r.stdout.strip() == "FAIL: the thing should have been denied"
    assert "SECRET-MESSAGE" not in r.stdout + r.stderr


def test_verdict_fails_for_another_reason_and_prints_codes_only():
    r = run_verdict(f"echo 'ERROR: (SomethingElse) {SECRET_TEXT}' >&2; exit 1", "AuthorizationFailed")
    assert r.returncode == 1
    assert r.stdout.strip() == "FAIL: failed for another reason: (SomethingElse)"
    assert "SECRET-MESSAGE" not in r.stdout + r.stderr


def test_verdict_prints_json_style_codes_too():
    r = run_verdict(f'echo \'{{"code": "InvalidTemplateDeployment", "message": "{SECRET_TEXT}"}}\'; exit 1', "AuthorizationFailed")
    assert r.returncode == 1
    assert '"code": "InvalidTemplateDeployment"' in r.stdout
    assert "SECRET-MESSAGE" not in r.stdout


def test_verdict_passes_on_a_nested_expected_code():
    cmd = f"echo 'ERROR: (DeploymentFailed) Code: RequestDisallowedByPolicy {SECRET_TEXT}' >&2; exit 1"
    r = run_verdict(cmd, "RequestDisallowedByPolicy")
    assert r.returncode == 0
    assert r.stdout.startswith("PASS:")
    assert "SECRET-MESSAGE" not in r.stdout + r.stderr


def test_verdict_with_require_also_needs_both_texts():
    cmd = "echo 'ERROR: (RequestDisallowedByPolicy) policyAssignments/some-other-rule' >&2; exit 1"
    r = run_verdict(cmd, "RequestDisallowedByPolicy", require_also="allowed-locations")
    assert r.returncode == 1 and "not by the expected rule" in r.stdout
    cmd = "echo 'ERROR: (RequestDisallowedByPolicy) policyAssignments/allowed-locations' >&2; exit 1"
    assert run_verdict(cmd, "RequestDisallowedByPolicy", require_also="allowed-locations").returncode == 0


def test_verdict_does_not_pass_on_resource_group_not_found_when_only_authorization_failed_is_wanted():
    r = run_verdict("echo 'ERROR: (ResourceGroupNotFound) x' >&2; exit 1", "AuthorizationFailed")
    assert r.returncode == 1 and "failed for another reason" in r.stdout


def test_oidc_setup_guide_has_the_critical_details():
    text = (FOUR_H / "OIDC-SETUP.md").read_text(encoding="utf-8")
    for needle in [
        "Other issuer",
        "repo:DK1051@<OWNER_ID>/td-4-cloud@<REPO_ID>:ref:refs/heads/main",
        "api://AzureADTokenExchange",
        "https://token.actions.githubusercontent.com",
        "api.github.com/repos/DK1051/td-4-cloud",
        "owner.id",
        "July 15, 2026",
        "rename",
        "GitHub Actions deploying Azure resources",
        "https://docs.github.com/en/actions/reference/security/oidc",
        "AADSTS70021",
        "AADSTS700016",
        "AuthorizationFailed",
        "MissingSubscriptionRegistration",
        "Check this format on the GitHub docs page above",
    ]:
        assert needle in text, needle
