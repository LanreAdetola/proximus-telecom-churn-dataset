// ---------------------------------------------------------------------------
// RBAC role assignments for the Azure ML workspace managed identity
// Identity-based auth — workspace MI gets least-privilege access.
// ---------------------------------------------------------------------------

@description('Principal ID of the workspace system-assigned managed identity')
param workspacePrincipalId string

@description('Name of the storage account to grant access to')
param storageAccountName string

@description('Name of the key vault to grant access to')
param keyVaultName string

@description('Name of the container registry to grant access to')
param acrName string

// ---------------------------------------------------------------------------
// Built-in role definition IDs
// ---------------------------------------------------------------------------
var storageBlobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var keyVaultSecretsOfficer     = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'
var acrPull                    = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

// ---------------------------------------------------------------------------
// Existing resources
// ---------------------------------------------------------------------------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' existing = {
  name: acrName
}

// ---------------------------------------------------------------------------
// Storage: Blob Data Contributor
// ---------------------------------------------------------------------------
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, workspacePrincipalId, storageBlobDataContributor)
  scope: storageAccount
  properties: {
    principalId: workspacePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributor)
  }
}

// ---------------------------------------------------------------------------
// Key Vault: Secrets Officer
// ---------------------------------------------------------------------------
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, workspacePrincipalId, keyVaultSecretsOfficer)
  scope: keyVault
  properties: {
    principalId: workspacePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsOfficer)
  }
}

// ---------------------------------------------------------------------------
// ACR: AcrPull
// ---------------------------------------------------------------------------
resource acrRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, workspacePrincipalId, acrPull)
  scope: acr
  properties: {
    principalId: workspacePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPull)
  }
}
