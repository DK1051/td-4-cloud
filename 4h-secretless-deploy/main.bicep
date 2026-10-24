// 4H: one locked-down storage account. Applied by the "4H deploy" workflow, never by hand.

@description('Azure region. The 4E policy only allows canadacentral and canadaeast.')
param location string = 'canadacentral'

@description('Value of the required owner tag (the 4E policy denies resources without it).')
param owner string

// Storage account names must be globally unique, 3-24 characters, lowercase letters and digits only.
// 'td4h' (4 characters) + uniqueString (13 characters) = 17 characters.
var storageAccountName = 'td4h${uniqueString(resourceGroup().id)}'

// 2026-06-01 is the newest API version that Bicep 0.48.1 knows without a BCP081 warning
// (tested by building with newer versions; every later one tried, 2026-07-01 onward, gave BCP081).
resource storage 'Microsoft.Storage/storageAccounts@2026-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: {
    owner: owner
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// Only the name is output. The resource ID contains the subscription ID, and workflow logs are public.
output storageAccountName string = storage.name
