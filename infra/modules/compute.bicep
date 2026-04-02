// ---------------------------------------------------------------------------
// Compute placeholder
// ---------------------------------------------------------------------------

@description('Name of the parent Azure ML workspace')
param workspaceName string

@description('Azure region')
param location string

@description('Environment tier')
@allowed(['dev', 'prod'])
param environment string

@description('Indicates that compute provisioning is deferred')
output computeProvisioningStatus string = 'Compute provisioning is deferred for ${workspaceName} (${environment}) in ${location}'
