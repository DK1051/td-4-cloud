# 4E Canada-Only Landing Zone

## What this is
A *landing zone* is the set of rules you put on a cloud account on day one, before you build anything in it, so that mistakes and attackers both hit a wall. This project sets four rules on a brand-new Microsoft Azure subscription (a *subscription* is the billing account that holds all your Azure resources) for the fictional Maple Harbour Credit Union (`mapleharbour.example`):

1. **Policy: keep resources in Canada.** A *policy* is a rule Azure checks every time something is created; this one refuses anything outside the regions `canadacentral` and `canadaeast`. Two built-in policies do the job: "Allowed locations" and "Allowed locations for resource groups".
2. **Policy: every resource needs an owner.** A *tag* is a name=value label on a resource. The built-in policy "Require a tag on resources" refuses any resource that has no `owner` tag, so nothing is created without a name attached.
3. **A limited role.** A *role* is a named bundle of permissions. "Portfolio Operator (td-4)" can read everything and start, stop and deallocate virtual machines, and nothing else. A *scope* is where a role or policy applies; this role is limited to one subscription.
4. **A budget and an alert.** A monthly spending budget with e-mail alerts, and an alert that fires when anyone is given new permissions, because that is the first thing an attacker with a stolen account does.

Nothing in this folder was run against Azure by Claude. Every file is applied by Eojin himself in Azure Cloud Shell after the pull request is merged.

## Files

| File | What it is |
|---|---|
| `policies/allowed-locations.parameters.json` | Settings for "Allowed locations" and "Allowed locations for resource groups": only `canadacentral` and `canadaeast`. |
| `policies/require-tags.parameters.json` | Settings for "Require a tag on resources": the tag name `owner`. |
| `roles/portfolio-operator.json` | The custom role. Its scope is a placeholder; the real one goes only in a git-ignored local copy. |
| `BUDGET-AND-ALERTS.md` | Portal steps for the budget and the role-assignment alert. |
| `SIGNUP.md` | Rules for signing up for the Azure free account. |
| `diagram.md` | A picture of how the pieces connect. |
| `../tests/test_4e_files.py` | Automatic checks of the files above (run in CI on every pull request). |

## Policy names confirmed from Microsoft's public repository
I read these three files from the `Azure/azure-policy` repository on GitHub (branch `master`, accessed 2026-10-22) and used only the `displayName` and `parameters` fields. I did not copy the policy definition IDs anywhere; the commands below look the definitions up by display name.

| Display name | Parameter used | Other parameter | Source file |
|---|---|---|---|
| Allowed locations | `listOfAllowedLocations` | `effect` (default Deny) | https://raw.githubusercontent.com/Azure/azure-policy/master/built-in-policies/policyDefinitions/General/AllowedLocations_Deny.json |
| Allowed locations for resource groups | `listOfAllowedLocations` | `effect` (default Deny) | https://raw.githubusercontent.com/Azure/azure-policy/master/built-in-policies/policyDefinitions/General/ResourceGroupAllowedLocations_Deny.json |
| Require a tag on resources | `tagName` | none | https://raw.githubusercontent.com/Azure/azure-policy/master/built-in-policies/policyDefinitions/Tags/RequireTag_Deny.json |

Both location files list exactly two parameters when re-fetched on 2026-10-22: `listOfAllowedLocations` (type Array) and `effect` (type String, default `Deny`, allowed values Audit, Deny, Disabled). Because the two location policies use the same parameter name, one parameter file serves both. `effect` is already Deny by default, so the parameter files do not set it.

## How I apply it
Do `SIGNUP.md` first. Then open Azure Cloud Shell (portal, the Cloud Shell icon, **Bash**, **No storage account required**). Cloud Shell is already signed in, so there is no `az login`, and you never type an ID: the commands look the subscription up for you.

```bash
git clone https://github.com/DK1051/td-4-cloud && cd td-4-cloud/4e-canada-landing-zone
SCOPE="/subscriptions/$(az account show --query id -o tsv)"
```

**Step 1. Policies.** The helper below looks a built-in definition up by its display name and stops with a message unless it finds exactly one (an empty or doubled answer would assign the wrong thing). The `--query name -o tsv` part prints only the assignment name, so no subscription ID appears on screen.

```bash
assign() {  # $1 = assignment name, $2 = built-in definition display name, $3 = parameter file
  DEF=$(az policy definition list --query "[?displayName=='$2' && policyType=='BuiltIn'].name" -o tsv)
  if [ "$(printf '%s\n' "$DEF" | grep -c .)" -ne 1 ]; then
    echo "STOP: expected exactly one built-in definition named '$2'. Ask Claude."; return 1
  fi
  az policy assignment create --name "$1" --display-name "$2 (td-4)" \
    --policy "$DEF" --params "@$3" --scope "$SCOPE" --query name -o tsv
}
assign allowed-locations    "Allowed locations"                      policies/allowed-locations.parameters.json
assign allowed-locations-rg "Allowed locations for resource groups"  policies/allowed-locations.parameters.json
assign require-owner-tag    "Require a tag on resources"             policies/require-tags.parameters.json
```

New assignments do not start enforcing instantly. `TODO(verify)`: the documented delay (Microsoft Learn, Azure Policy evaluation triggers). 4H's test that a deployment to `westus` is refused only proves something once the policies are in force.

**Step 2. The resource group.** The alert and its action group (Step 4) need a resource group (a named container for related resources), and it must be in Canada or our own policy refuses it. Replace `<your-name>` with your name:

```bash
az group create --name rg-td4-canada --location canadacentral --tags owner=<your-name> -o none
```

**Step 3. The custom role** (the `sed` command puts your subscription into a local copy that git ignores):

```bash
# '#' is the sed separator because the scope contains '/'
sed "s#<SUBSCRIPTION_ID>#$(az account show --query id -o tsv)#" roles/portfolio-operator.json > roles/portfolio-operator.local.json
az role definition create --role-definition @roles/portfolio-operator.local.json --query roleName -o tsv
```

If the role already exists (you are re-running this), `create` is refused; update it instead:

```bash
az role definition update --role-definition @roles/portfolio-operator.local.json --query roleName -o tsv
```

**Step 4. Budget and alert** in the portal: follow `BUDGET-AND-ALERTS.md`. Add the `owner` tag in every wizard and choose `rg-td4-canada` as the resource group.

## What Eojin did / what Claude did

| Who | What |
|---|---|
| Claude | Confirmed the policy names and parameter names from Microsoft's public repository, wrote every file in this folder and the automatic tests, and wrote this README. Claude never connected to Azure. |
| Eojin | Signs up for the Azure free account, runs the commands above in Cloud Shell, follows `BUDGET-AND-ALERTS.md` in the portal, and fills in the Results table below. Not done yet (the status in the repository README stays "Built" until he has). |

## Results
Fill in after applying. Crop every ID out of screenshots; no raw portal exports.

| Control | Date applied | How I checked |
|---|---|---|
| Allowed locations | | |
| Allowed locations for resource groups | | |
| Require `owner` tag | | |
| Custom role "Portfolio Operator (td-4)" | | |
| Monthly budget (50%, 80%, 100%) | | |
| Role-assignment alert | | |

## Limits
- Not tested against Azure. The automatic tests only check the JSON files; Eojin's manual run is the real test.
- The location policy skips resources whose location is `global`, and the tag policy does not apply to resource groups (both stated in Microsoft's own descriptions in the source files above). So a tag on resource groups is not enforced by this project.
- Mounting a Cloud Shell storage account later will be denied unless the account is in Canada and has an `owner` tag.
- A policy only stops new actions; it does not delete anything that already exists.
- Whether a budget is available on a free-trial subscription is `TODO(verify)`.
- The free-account terms and sign-up URL are `TODO(verify)` on sign-up day.
- This project mirrors the intent of the Government of Canada data-residency direction. It does NOT claim compliance with it or with any other standard.

## Sources
- Canadian Centre for Cyber Security, alert AL26-010: https://www.cyber.gc.ca/en/alerts-advisories/al26-010-cyber-criminals-social-engineering-enabled-compromise-enterprise-saas-environments
- Government of Canada data-residency direction: `TODO(verify)` URL (it is not in this repository). The direction is archived and replaced by requirement 4.4.3.14; this project mirrors its intent and claims no compliance.
- Microsoft built-in policy definitions: the three source files listed above.
