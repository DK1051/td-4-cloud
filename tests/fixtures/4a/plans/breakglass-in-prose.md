=== INC-01 ===
# DRY RUN: Microsoft Graph PowerShell: Get-MgAuditLogSignIn -Filter "userId eq '<object-id>'"
# DRY RUN: Microsoft Graph PowerShell: Get-MgAuditLogDirectoryAudit -Filter "targetResources/any(t: t/id eq '<object-id>')"
# DRY RUN: Microsoft Graph PowerShell: Revoke-MgUserSignInSession -UserId <object-id>
# DRY RUN: Microsoft Graph PowerShell: Remove-MgUserAuthenticationPhoneMethod -UserId <object-id> -PhoneAuthenticationMethodId <object-id>
# DRY RUN: Azure CLI: az role assignment delete --assignee <object-id> --role "not in the report"
# DRY RUN: Microsoft Graph PowerShell: Update-MgUser -UserId <object-id> -AccountEnabled:$false
The break-glass accounts bg-admin-01@mapleharbour.example and bg-admin-02@mapleharbour.example were left untouched.
Note for the reviewer: nothing is purged and the user is not deleted.
=== END ===

Never-touch list checked — no command targets a break-glass account
