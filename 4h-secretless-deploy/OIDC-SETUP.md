# OIDC setup guide (do this once, by hand, after the merge)

This guide connects GitHub to your Azure account so the "4H deploy" and "4H cannot-do" workflows can log in without any stored password. Follow the steps in order. Nothing in this repository ever holds an ID: wherever you see `<OWNER_ID>`, `<REPO_ID>` or similar, you type your own value into the Azure or GitHub page, not into a file.

Portal and GitHub screens get renamed now and then. If a label differs slightly, go by what it does.

## 1. What OIDC is, and why there is no stored secret
OpenID Connect (OIDC) lets GitHub hand Azure a short-lived signed token that says "this is workflow X in repository Y on branch main". Azure accepts the token only if a *federated credential* (a rule you pre-register in Azure that names exactly that repository and branch) matches it. The token lives for minutes and is created fresh on every run, so there is no password or key to store, leak or rotate.

## 2. Step A: get two numbers from GitHub
Open `https://api.github.com/repos/DK1051/td-4-cloud` in your browser. Find two fields:
- `owner.id` (inside the `owner` block): this is `<OWNER_ID>`.
- `id` (a top-level field): this is `<REPO_ID>`.

Keep both numbers out of the repository (house rule). They go only into the federated credential in Step C.

## 3. Step B: register an app in Microsoft Entra ID
An *app registration* is the identity the workflow will log in as.
1. Azure portal, then **Microsoft Entra ID**, then **App registrations**, then **New registration**.
2. Name: `td-4-cloud-github-oidc`. Supported account types: **single tenant**. Leave the redirect URI empty.
3. Click **Register**. On the overview page copy **Application (client) ID** and **Directory (tenant) ID** straight into GitHub secrets (Step D) and nowhere else: not a file, not a chat, not a screenshot.

## 4. Step C (CRITICAL): the federated credential
1. In the app: **Certificates & secrets**, then **Federated credentials**, then **Add credential**.
2. Scenario: choose **"Other issuer"**.

> **Do NOT use the portal's "GitHub Actions deploying Azure resources" template.** It may build the old name-only subject `repo:DK1051/td-4-cloud:ref:refs/heads/main`, which does not match the token a repository created after July 15, 2026 sends. The login then fails with `AADSTS70021` and the cause is hard to see.

3. Fill in exactly:
   - **Issuer:** `https://token.actions.githubusercontent.com`
   - **Subject identifier:** `repo:DK1051@<OWNER_ID>/td-4-cloud@<REPO_ID>:ref:refs/heads/main` with both numbers filled in from Step A and no spaces.
   - **Audience:** `api://AzureADTokenExchange`
   - **Name:** `github-main`

**Check this format on the GitHub docs page above before you create the credential — this guide's author could not open that page from the cloud session. If the page shows a different format, the page wins.** The page is https://docs.github.com/en/actions/reference/security/oidc. The subject above is GitHub's immutable format (it contains the numeric owner and repository IDs), used by repositories created after July 15, 2026. If the page describes it differently, use the page's format and tell Claude at the next session so this guide is corrected.

## 5. Never rename the repository
**Never rename the repository after this.** The subject contains the repository name, so a rename breaks the match and every login fails. Do not rename the owner account either. If this ever happens, fix the subject in the federated credential; do not recreate the repository.

## 6. Step D: put the three values into GitHub secrets
GitHub, then the repository's **Settings**, then **Secrets and variables**, then **Actions**, then **New repository secret**. Create three secrets, with exactly these names:
- `AZURE_CLIENT_ID` (the Application (client) ID from Step B)
- `AZURE_TENANT_ID` (the Directory (tenant) ID from Step B)
- `AZURE_SUBSCRIPTION_ID` (portal, then **Subscriptions**, then your subscription)

## 7. Step E: prepare the Azure side
Do the first part once, as yourself, in Azure Cloud Shell (portal, the Cloud Shell icon, **Bash**). Cloud Shell is already signed in.
1. Register the storage provider. The deploy identity is not allowed to do this itself:
   ```bash
   az provider register --namespace Microsoft.Storage
   az provider show --namespace Microsoft.Storage --query registrationState -o tsv
   ```
   Repeat the second command every minute or so until it prints `Registered` (a few minutes).
2. Make sure the 4E policies are assigned first (see `4e-canada-landing-zone/README.md`). Then create the two resource groups:
   ```bash
   az group create --name rg-td4-canada --location canadacentral --tags owner=<your-name> -o none
   az group create --name rg-td4-private --location canadacentral --tags owner=<your-name> -o none
   ```
   (`-o none` keeps the output, which contains your subscription ID, off the screen.)
3. Give the app the **Contributor** role on `rg-td4-canada` only. In the portal: open the resource group `rg-td4-canada`, then **Access control (IAM)**, then **Add role assignment**, role **Contributor**, members **"User, group, or service principal"**, and search for `td-4-cloud-github-oidc`.
4. Do not assign anything on `rg-td4-private`. The cannot-do test relies on the identity having no access there.

## 8. Step F: run the workflows
1. GitHub, then the **Actions** tab, then **4H deploy**, then **Run workflow** on the `main` branch. Expect the log to end with `Succeeded`.
2. Then **4H cannot-do**, **Run workflow** on `main`. Expect three `PASS` lines (one for each of the three checks).
3. Paste the run links and outcomes into the Results table in `4h-secretless-deploy/README.md`. Links are public and safe; raw output is not.

The workflows must run from `main`: the federated credential pins that branch, so a run from any other branch fails to log in by design.

## 9. Troubleshooting
| What you see | What it means | What to do |
|---|---|---|
| `AADSTS70021` | No federated credential matches the token's subject. | Re-check the owner ID, the repository ID, the branch and the exact spelling in Step C; the workflow must run from `main`. |
| `AADSTS700016` | Wrong client ID or tenant ID. | Re-copy the two values from the app's overview page into the secrets. |
| `AuthorizationFailed` on the deploy | The Contributor assignment is missing, or not yet active. | Check Step E part 3, wait a few minutes, run again. |
| `MissingSubscriptionRegistration` | The Microsoft.Storage registration (Step E part 1) is not done. | Finish it and wait for `Registered`. |

Optional debugging, to see exactly what subject GitHub sends: temporarily add this step to a workflow that has `permissions: id-token: write`, run it once, read the printed `sub`, then remove the step and delete that run from the Actions tab (the line contains your two numbers, and public logs are public).
```yaml
      - uses: actions/github-script@<LATEST_MAJOR>
        with:
          script: |
            const t = await core.getIDToken('api://AzureADTokenExchange');
            const body = JSON.parse(Buffer.from(t.split('.')[1], 'base64url').toString());
            core.info('sub = ' + body.sub);
```
`TODO(verify)`: replace `<LATEST_MAJOR>` with the latest major version of `actions/github-script`, checked on its GitHub page; do not guess it.

## 10. Logs on a public repository are public
GitHub masks the three secret values and nothing else. That is why the workflows print only error codes. Never paste raw workflow output into the README, an issue or a chat; crop every ID out of screenshots.
