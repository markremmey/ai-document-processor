@description('Name of the resource.')
param name string
@description('Location to deploy the resource. Defaults to the location of the resource group.')
param location string = resourceGroup().location
@description('Tags for the resource.')
param tags object = {}

param publicNetworkAccessForIngestion string = 'Enabled'
param publicNetworkAccessForQuery string = 'Enabled'

param suffix string

@description('Name for the Log Analytics Workspace resource associated with the Application Insights instance.')
param logAnalyticsWorkspaceId string

var abbrs = loadJsonContent('../../abbreviations.json')

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = if ( empty(logAnalyticsWorkspaceId) ) {
  name: '${abbrs.managementGovernance.logAnalyticsWorkspace}${suffix}'
  location: location
  properties: {
    sku: {
      name: 'pergb2018'
    }
    retentionInDays: 30
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: publicNetworkAccessForIngestion
    publicNetworkAccessForQuery: publicNetworkAccessForQuery
  }
}

@description('ID for the deployed Application Insights resource.')
output id string = applicationInsights.id
@description('Name for the deployed Application Insights resource.')
output name string = applicationInsights.name
@description('Instrumentation Key for the deployed Application Insights resource.')
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
@description('Connection string for the deployed Application Insights resource.')
output connectionString string = applicationInsights.properties.ConnectionString
