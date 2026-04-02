// ---------------------------------------------------------------------------
// Proximus Churn MLOps — Azure ML Workspace + supporting resources
// Identity-based auth throughout — no stored keys.
// ---------------------------------------------------------------------------

targetScope = 'resourceGroup'

@description('Environment name used for naming convention')
@allowed(['dev'])
param environment string

@description('Azure region')
param location string = resourceGroup().location

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------
var storageAccountName = 'mlwproxistorage77490c958'
var keyVaultName = 'mlwproxikeyvaultdabe594b'
var appInsightsName = 'mlwproxiinsightsaf4152a4'
var logAnalyticsName = 'mlwproxilogalyti58823f50'
var workspaceName = 'mlw-proximus-churn-dev'

// ---------------------------------------------------------------------------
// Storage Account (identity-based access — no account keys)
// ---------------------------------------------------------------------------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false          // identity-based only
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource churnContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'churn-data'
}

// ---------------------------------------------------------------------------
// Key Vault (RBAC-based access — no vault access policies)
// ---------------------------------------------------------------------------
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
  }
}

// ---------------------------------------------------------------------------
// Log Analytics + Application Insights
// ---------------------------------------------------------------------------
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// ---------------------------------------------------------------------------
// Azure ML Workspace (system-assigned managed identity)
// ---------------------------------------------------------------------------
resource workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: workspaceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'Proximus Churn ${toUpper(environment)}'
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
  }
}

// ---------------------------------------------------------------------------
// RBAC for workspace managed identity (module)
// ---------------------------------------------------------------------------
module rbac 'modules/rbac.bicep' = {
  name: 'rbac-${environment}'
  params: {
    workspacePrincipalId: workspace.identity.principalId
    storageAccountName: storageAccount.name
    keyVaultName: keyVault.name
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
output workspaceName string = workspace.name
output workspaceId string = workspace.id
output storageAccountName string = storageAccount.name
