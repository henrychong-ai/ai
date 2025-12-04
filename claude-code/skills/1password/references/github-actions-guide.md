# GitHub Actions Integration Guide

## Overview

The 1Password GitHub Action (`1password/load-secrets-action`) enables secure secret management in CI/CD workflows. Secrets are loaded from your 1Password vault and automatically masked in GitHub Actions logs.

### Key Features
- Load secrets directly from 1Password vaults
- Automatic log masking (sensitive values replaced with `***`)
- Two authentication methods: Service Accounts or Connect Server
- Real-time sync with vault changes

## Prerequisites

- 1Password account with vault access
- GitHub repository with Actions enabled
- Either:
  - Service Account token (recommended for most users)
  - Connect Server deployment (self-hosted option)

## Authentication Methods

### Service Account (Recommended)

Best for: Most CI/CD use cases, quick setup, cloud-hosted.

**Setup:**
1. Create a service account at 1Password.com → Developer
2. Grant vault access to the service account
3. Store token as GitHub secret: `OP_SERVICE_ACCOUNT_TOKEN`

### Connect Server

Best for: Self-hosted environments, air-gapped networks, custom infrastructure.

**Setup:**
1. Deploy 1Password Connect Server
2. Store host URL and token as GitHub secrets:
   - `OP_CONNECT_HOST`
   - `OP_CONNECT_TOKEN`

## Workflow Configuration

### Basic Setup with Service Account

```yaml
name: Deploy with 1Password Secrets

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Configure 1Password
      - uses: 1password/load-secrets-action/configure@v1
        with:
          service-account-token: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}

      # Load secrets
      - uses: 1password/load-secrets-action@v1
        with:
          secret-DOCKERHUB_USERNAME: op://app-cicd/docker/username
          secret-DOCKERHUB_TOKEN: op://app-cicd/docker/token

      # Use secrets in subsequent steps
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ env.DOCKERHUB_USERNAME }}
          password: ${{ env.DOCKERHUB_TOKEN }}
```

### Setup with Connect Server

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: 1password/load-secrets-action/configure@v1
        with:
          connect-host: ${{ secrets.OP_CONNECT_HOST }}
          connect-token: ${{ secrets.OP_CONNECT_TOKEN }}

      - uses: 1password/load-secrets-action@v1
        with:
          secret-API_KEY: op://vault-name/item-name/api-key
```

### Multiple Secrets Example

```yaml
- uses: 1password/load-secrets-action@v1
  with:
    secret-AWS_ACCESS_KEY_ID: op://app-cicd/aws/access-key-id
    secret-AWS_SECRET_ACCESS_KEY: op://app-cicd/aws/secret-access-key
    secret-DATABASE_URL: op://app-cicd/database/connection-string
    secret-DEPLOY_KEY: op://app-cicd/deploy/ssh-key
```

### Step-Scoped Token Access

For tighter security, scope the token to specific steps:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Only this step has access to 1Password
      - name: Build with secrets
        uses: 1password/load-secrets-action@v1
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}
        with:
          secret-API_KEY: op://vault/item/key

      # Subsequent steps don't have vault access
      - name: Run tests
        run: npm test
```

## Secret Reference Syntax

Format: `op://vault-name/item-name/field-name`

### Examples

| Reference | Description |
|-----------|-------------|
| `op://app-cicd/docker/username` | Docker username in app-cicd vault |
| `op://Production/aws/secret-access-key` | AWS secret in Production vault |
| `op://CI-Secrets/GitHub/token` | GitHub token in CI-Secrets vault |

### Using Item IDs

For items with special characters or duplicates, use the unique identifier:

```yaml
secret-API_KEY: op://vault-name/abc123xyz/api-key
```

Find item ID: `op item get "ItemName" --vault="VaultName" --format=json | jq '.id'`

## Security Features

### Automatic Log Masking

All secrets loaded by the action are automatically masked in logs:

```
Run echo $API_KEY
***
```

GitHub replaces any occurrence of the secret value with `***`.

### Service Account Best Practices

1. **Least privilege**: Create separate service accounts per workflow
2. **Vault scoping**: Limit service account to specific vaults only
3. **Token rotation**: Rotate tokens quarterly
4. **Step scoping**: Use `env` at step level, not job level

## Platform Support

| Runner | Supported |
|--------|-----------|
| `ubuntu-latest` | Yes |
| `macos-latest` | Yes |
| `windows-latest` | **No** |

**Important:** Windows runners are not supported. Use Linux or macOS runners.

## Troubleshooting

### "Cannot create item in piped environment"

**Symptom:** CLI commands fail when output is piped.

**Solution:** Use JSON templates instead of direct CLI input:

```yaml
- name: Create item via JSON
  run: |
    echo '{"title":"NewItem","category":"LOGIN","fields":[{"id":"username","type":"STRING","value":"user"}]}' | op item create --template=-
```

### "Invalid service account token"

**Solutions:**
1. Verify token is stored correctly in GitHub secrets
2. Check token hasn't expired
3. Ensure service account has vault access

### "Item not found"

**Solutions:**
1. Verify vault and item names match exactly (case-sensitive)
2. Check service account has access to the vault
3. Use item ID instead of name if special characters present

### Secrets Not Available in Subsequent Steps

**Cause:** Secrets are exported as environment variables, not GitHub outputs.

**Solution:** Ensure you reference them as `${{ env.SECRET_NAME }}`, not outputs:

```yaml
# Correct
- run: echo ${{ env.API_KEY }}

# Wrong
- run: echo ${{ steps.load-secrets.outputs.API_KEY }}
```

## Complete Workflow Example

```yaml
name: Production Deployment

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Configure 1Password
        uses: 1password/load-secrets-action/configure@v1
        with:
          service-account-token: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}

      - name: Load deployment secrets
        uses: 1password/load-secrets-action@v1
        with:
          secret-AWS_ACCESS_KEY_ID: op://Production/aws/access-key-id
          secret-AWS_SECRET_ACCESS_KEY: op://Production/aws/secret-access-key
          secret-DOCKER_USERNAME: op://Production/docker/username
          secret-DOCKER_TOKEN: op://Production/docker/token
          secret-DATABASE_URL: op://Production/database/url

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ env.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ env.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ env.DOCKER_USERNAME }}
          password: ${{ env.DOCKER_TOKEN }}

      - name: Build and push
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster prod --service myapp --force-new-deployment
```

## Related Resources

- [1Password Service Accounts](https://developer.1password.com/docs/service-accounts/)
- [GitHub Actions Marketplace](https://github.com/marketplace/actions/load-secrets-from-1password)
- [1Password Connect](https://developer.1password.com/docs/connect/)
