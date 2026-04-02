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

// ---------------------------------------------------------------------------
// Built-in role definition IDs
// ---------------------------------------------------------------------------
var storageBlobDataContributorGuid = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var keyVaultSecretsOfficerGuid     = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'

// Full role definition resource IDs (used for both name determinism and assignment)
var storageBlobDataContributorRoleDefId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorGuid)
var keyVaultSecretsOfficerRoleDefId     = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsOfficerGuid)

// ---------------------------------------------------------------------------
// Existing resources
// ---------------------------------------------------------------------------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// ---------------------------------------------------------------------------
// Storage: Blob Data Contributor
// ---------------------------------------------------------------------------
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, workspacePrincipalId, storageBlobDataContributorRoleDefId)
  scope: storageAccount
  properties: {
    principalId: workspacePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: storageBlobDataContributorRoleDefId
  }
}

// ---------------------------------------------------------------------------
// Key Vault: Secrets Officer
// ---------------------------------------------------------------------------
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, workspacePrincipalId, keyVaultSecretsOfficerRoleDefId)
  scope: keyVault
  properties: {
    principalId: workspacePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultSecretsOfficerRoleDefId
  }
}

