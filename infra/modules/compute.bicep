// ---------------------------------------------------------------------------
// Compute: training cluster + dev compute instance
// ---------------------------------------------------------------------------

@description('Name of the parent Azure ML workspace')
param workspaceName string

@description('Azure region')
param location string

@description('Environment tier')
@allowed(['dev', 'prod'])
param environment string

resource workspace 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = {
  name: workspaceName
}

// ---------------------------------------------------------------------------
// Training cluster (auto-scales to 0 when idle)
// ---------------------------------------------------------------------------
resource trainingCluster 'Microsoft.MachineLearningServices/workspaces/computes@2024-04-01' = {
  parent: workspace
  name: 'cpu-cluster'
  location: location
  properties: {
    computeType: 'AmlCompute'
    properties: {
      vmSize: environment == 'prod' ? 'Standard_DS4_v2' : 'Standard_DS3_v2'
      minNodeCount: 0
      maxNodeCount: environment == 'prod' ? 4 : 2
      idleTimeBeforeScaleDown: 'PT10M'
      remoteLoginPortPublicAccess: 'Disabled'
    }
  }
}

// ---------------------------------------------------------------------------
// Dev compute instance (dev only)
// ---------------------------------------------------------------------------
resource devInstance 'Microsoft.MachineLearningServices/workspaces/computes@2024-04-01' = if (environment == 'dev') {
  parent: workspace
  name: 'dev-instance'
  location: location
  properties: {
    computeType: 'ComputeInstance'
    properties: {
      vmSize: 'Standard_DS2_v2'
      idleTimeBeforeShutdown: 'PT30M'
      enableNodePublicIp: false
    }
  }
}
