# Budget and "new permissions" alert (portal steps)

> **WARNING, read before you click anything.** Every portal wizard has a **Tags** tab. On each one, add the tag `owner` = your name. If you skip it, your own 4E tag policy ("Require a tag on resources") will deny the action group and the alert rule, and the action will be refused by the policy. (A *tag* is a name=value label attached to an Azure resource; the policy refuses any resource that has no `owner` label.)

Do this after the policies are applied (see `README.md`) and after you have signed up (see `SIGNUP.md`). Portal labels change from time to time; if a button is named slightly differently, go by what it does. Nothing here needs a command or an ID.

## Part A. A monthly budget with three alerts

A *budget* in Azure does not stop spending. It only e-mails you when your spending crosses a line you chose, so a mistake costs you cents instead of dollars.

Is a budget available on a free-trial subscription? `TODO(verify)`: check on sign-up day. If the portal does not offer it, skip Part A, do Part B, and add a line to `docs/CAVEATS.md`.

1. In the Azure portal search bar, type **Subscriptions** and open your subscription.
2. In the left menu open **Cost Management** and then **Budgets**, then click **Add**.
3. Name it `td4-monthly`. Set the reset period to **Monthly**, and the amount to **$10** (a small number is the point; you may pick another).
4. On the **Set alerts** step add three alert conditions, each on **Actual** cost:
   - 50% of the budget
   - 80% of the budget
   - 100% of the budget
5. For each one, enter your own e-mail address as the alert recipient. (Your address is not written in this repository on purpose.)
6. On the **Tags** tab (if the wizard shows one), add `owner` = your name.
7. Click **Create**.

Why three levels: 50% is "look at it today", 80% is "something is running that should not be", 100% is "stop and clean up".

## Part B. An alert when someone is given new permissions

This one watches Azure's *activity log* (the diary where Azure records every change made to your subscription).

### Why a role assignment write is the signal
A *role assignment* is the record that says "this account gets this role in this place". An attacker who has stolen an account usually gives themselves more power first, and doing that creates a role assignment, so the activity log shows the operation `Microsoft.Authorization/roleAssignments/write` ("Create role assignment"). You will normally make very few of these yourself, so any surprise is worth a look.

### Steps
1. In the portal search bar type **Monitor** and open it, then open **Alerts**.
2. Click **Create** and then **Alert rule**.
3. **Scope**: choose your subscription.
4. **Condition**: click **See all signals**, search for **Create role assignment** (the operation `Microsoft.Authorization/roleAssignments/write`), select it, and leave the filters empty so every such event alerts. `TODO(verify on the day)`: the wizard's wording for this step.
5. **Actions**: click **Create action group** (an *action group* is the list of people and things Azure contacts when an alert fires).
   - Name it `ag-td4-email`.
   - On the **Notifications** tab choose **Email/SMS message/Push/Voice**, tick **Email**, and enter your own e-mail address.
   - On the **Tags** tab add `owner` = your name (see the warning above).
   - On the **Basics** tab, choose the resource group `rg-td4-canada` (created in README Step 2). Do not use "Create new": it may offer a region outside Canada, which your own policy would refuse.
   - Create it and make sure it is selected for the alert rule.
6. **Details**: name the rule `alert-role-assignment-write`, and choose the resource group `rg-td4-canada` (same reason as above).
7. **Tags** tab: add `owner` = your name.
8. Click **Review + create**, then **Create**.

### Check that it works
The alert fires the next time any role assignment is created in the subscription, for example when you later give the 4H deployment identity a role. Then wait a few minutes and look for the e-mail. `TODO(verify)`: how long Azure takes to deliver activity-log alerts. Record what you saw in the Results table of `README.md` (crop every ID out of screenshots).

## If something is refused
If the wizard fails with a message about policy, you probably forgot an `owner` tag or chose a region outside Canada. Fix the tag or the region and try again. That refusal is the 4E guard-rail working as intended.
