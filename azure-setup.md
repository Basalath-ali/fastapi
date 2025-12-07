# Azure Credentials Setup Guide

## Prerequisites
- Azure CLI installed (`az --version` to check)
- Logged into Azure (`az login`)
- Know your subscription ID, resource group, and AKS cluster name

## Step 1: Login to Azure CLI

```bash
az login
```

This will open a browser window for you to authenticate.

## Step 2: Set Your Subscription (if you have multiple)

```bash
# List all subscriptions
az account list --output table

# Set the subscription you want to use
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

## Step 3: Get Your Subscription ID

```bash
az account show --query id -o tsv
```

Save this subscription ID - you'll need it.

## Step 4: Create Service Principal with Contributor Role

Replace the placeholders with your actual values:

```bash
az ad sp create-for-rbac \
  --name "github-actions-fastapi" \
  --role contributor \
  --scopes /subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME} \
  --sdk-auth
```

**Example:**
```bash
az ad sp create-for-rbac \
  --name "github-actions-fastapi" \
  --role contributor \
  --scopes /subscriptions/12345678-1234-1234-1234-123456789abc/resourceGroups/my-aks-rg \
  --sdk-auth
```

### Alternative: Subscription-wide access (less secure)

```bash
az ad sp create-for-rbac \
  --name "github-actions-fastapi" \
  --role contributor \
  --scopes /subscriptions/{SUBSCRIPTION_ID} \
  --sdk-auth
```

## Step 5: Copy the Output

The command will output JSON like this:

```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**IMPORTANT:** Copy this ENTIRE JSON output. You'll paste it into GitHub secrets.

## Step 6: Get Your AKS Cluster Information

```bash
# Get resource group name
az aks list --output table

# Get specific cluster details
az aks show --name {AKS_CLUSTER_NAME} --resource-group {RESOURCE_GROUP_NAME}
```

---

## GitHub Secrets Setup

### Method 1: Via GitHub Web Interface

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Create These Secrets:

#### 1. AZURE_CREDENTIALS
- **Name:** `AZURE_CREDENTIALS`
- **Value:** Paste the ENTIRE JSON output from Step 5
- Click **Add secret**

#### 2. DOCKER_USERNAME
- **Name:** `DOCKER_USERNAME`
- **Value:** `basalath7ali`
- Click **Add secret**

#### 3. DOCKER_PASSWORD
- **Name:** `DOCKER_PASSWORD`
- **Value:** Your Docker Hub password or access token
- Click **Add secret**

### Method 2: Using GitHub CLI (gh)

```bash
# Set AZURE_CREDENTIALS (paste the JSON as a single line)
gh secret set AZURE_CREDENTIALS < azure-creds.json

# Set DOCKER_USERNAME
gh secret set DOCKER_USERNAME -b "basalath7ali"

# Set DOCKER_PASSWORD (will prompt for input)
gh secret set DOCKER_PASSWORD
```

---

## GitHub Variables Setup

### Via GitHub Web Interface:

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **Variables** tab
5. Click **New repository variable**

### Create These Variables:

#### 1. AKS_CLUSTER_NAME
- **Name:** `AKS_CLUSTER_NAME`
- **Value:** Your AKS cluster name (e.g., `my-aks-cluster`)
- Click **Add variable**

#### 2. AKS_RESOURCE_GROUP
- **Name:** `AKS_RESOURCE_GROUP`
- **Value:** Your Azure resource group name (e.g., `my-aks-rg`)
- Click **Add variable**

#### 3. KUBERNETES_NAMESPACE
- **Name:** `KUBERNETES_NAMESPACE`
- **Value:** `production` (or `default`, `staging`, etc.)
- Click **Add variable**

### Using GitHub CLI:

```bash
gh variable set AKS_CLUSTER_NAME -b "my-aks-cluster"
gh variable set AKS_RESOURCE_GROUP -b "my-aks-rg"
gh variable set KUBERNETES_NAMESPACE -b "production"
```

---

## Docker Hub Access Token (Recommended over Password)

Instead of using your Docker Hub password, create an access token:

1. Go to https://hub.docker.com/settings/security
2. Click **New Access Token**
3. Name it: `github-actions-fastapi`
4. Copy the token
5. Use this token as your `DOCKER_PASSWORD` secret

---

## Verify Setup

After creating all secrets and variables, verify:

```bash
# List secrets (values are hidden)
gh secret list

# List variables
gh variable list
```

You should see:
- ✅ AZURE_CREDENTIALS
- ✅ DOCKER_USERNAME
- ✅ DOCKER_PASSWORD
- ✅ AKS_CLUSTER_NAME
- ✅ AKS_RESOURCE_GROUP
- ✅ KUBERNETES_NAMESPACE

---

## Testing the Service Principal

Test if the service principal works:

```bash
# Login using service principal
az login --service-principal \
  -u {clientId} \
  -p {clientSecret} \
  --tenant {tenantId}

# Try to access your AKS cluster
az aks get-credentials \
  --resource-group {RESOURCE_GROUP_NAME} \
  --name {AKS_CLUSTER_NAME}

# Test kubectl access
kubectl get nodes
```

---

## Troubleshooting

### Error: "Insufficient privileges"
Grant the service principal AKS access:
```bash
az role assignment create \
  --assignee {clientId} \
  --role "Azure Kubernetes Service Cluster User Role" \
  --scope /subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.ContainerService/managedClusters/{AKS_CLUSTER_NAME}
```

### Error: "Service principal not found"
Wait a few minutes after creating the service principal, then try again.

### Error: "Invalid client secret"
Recreate the service principal or reset its credentials:
```bash
az ad sp credential reset --name {clientId}
```

---

## Security Best Practices

1. ✅ Use resource group scope (not subscription-wide)
2. ✅ Use Docker Hub access tokens (not passwords)
3. ✅ Rotate credentials regularly
4. ✅ Use environment protection rules in GitHub
5. ✅ Never commit credentials to git

---

## Quick Command Reference

```bash
# Get subscription ID
az account show --query id -o tsv

# List resource groups
az group list --output table

# List AKS clusters
az aks list --output table

# Get AKS credentials for kubectl
az aks get-credentials --resource-group {RG_NAME} --name {AKS_NAME}

# Delete service principal (cleanup)
az ad sp delete --id {clientId}
```
