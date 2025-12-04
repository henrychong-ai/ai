# AWS Secrets Manager Integration

## Overview

1Password Environments can sync secrets to AWS Secrets Manager, enabling centralized secrets management with automatic synchronization. This integration uses 1Password's Confidential Computing platform built on AWS Nitro Enclaves for secure credential handling.

### Use Cases

- Centralize secrets for applications running on AWS
- Share secrets with team without sharing AWS credentials
- Maintain single source of truth in 1Password
- Streamline secret distribution to AWS infrastructure

### How It Works

```
1Password Desktop App
        │
        │ (changes to environment)
        ▼
1Password Confidential Computing
(AWS Nitro Enclaves)
        │
        │ (secure sync)
        ▼
AWS Secrets Manager
        │
        ▼
Your AWS Applications
```

**Important:** Sync is one-directional only. Changes in AWS Secrets Manager do NOT sync back to 1Password.

## Prerequisites

Before setup, ensure you have:

- [ ] 1Password account with desktop app installed
- [ ] 1Password Developer enabled
- [ ] An environment created in 1Password
- [ ] AWS account with permissions to:
  - Create IAM Identity Providers
  - Create IAM Policies
  - Create IAM Roles
  - Create/Update Secrets Manager secrets
  - (Optional) Create KMS keys

## Setup Process

### Step 1: Open AWS Configuration

1. Open 1Password desktop app
2. Go to Developer → Environments
3. Select your environment
4. Click **Destinations** tab
5. Click **Configure destination** for AWS Secrets Manager

### Step 2: Register SAML Provider in AWS

1. In 1Password, click **Download SAML metadata**
2. Open AWS Console → IAM → Identity providers
3. Click **Add provider**
4. Select **SAML**
5. Provider name: `1Password-Secrets-Sync` (or your choice)
6. Upload the metadata file downloaded from 1Password
7. Click **Add provider**

### Step 3: Create IAM Policy

Create a policy allowing secret management:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:CreateSecret",
                "secretsmanager:UpdateSecret",
                "secretsmanager:PutSecretValue",
                "secretsmanager:TagResource"
            ],
            "Resource": "arn:aws:secretsmanager:*:*:secret:1password/*"
        }
    ]
}
```

**Note:** This policy scopes to secrets prefixed with `1password/`. Adjust as needed.

### Step 4: Create IAM Role

1. IAM → Roles → Create role
2. Select **SAML 2.0 federation**
3. SAML provider: Select the provider from Step 2
4. Select **Allow programmatic access only**
5. Attach the policy from Step 3
6. Name the role (e.g., `1Password-Secrets-Sync-Role`)
7. Copy the Role ARN for the next step

### Step 5: Configure in 1Password

1. Return to 1Password AWS configuration
2. Enter the Role ARN from Step 4
3. Select AWS region for the secret
4. Enter a unique secret name (e.g., `1password/my-project/env`)
5. (Optional) Configure KMS encryption key

### Step 6: Test Connection

1. Click **Test connection**
2. 1Password creates and deletes a test secret
3. If successful, proceed to enable
4. If failed, check IAM permissions

### Step 7: Enable Integration

1. Click **Enable integration**
2. Initial sync begins
3. Future changes sync automatically

## KMS Encryption (Optional)

For additional security, encrypt secrets with your own KMS key:

### Additional IAM Policy for KMS

Add to your policy:

```json
{
    "Effect": "Allow",
    "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:GenerateDataKey"
    ],
    "Resource": "arn:aws:kms:REGION:ACCOUNT:key/KEY-ID"
}
```

### Configure KMS in 1Password

1. In AWS destination settings
2. Enable **Use custom KMS key**
3. Enter KMS key ARN

## Sync Behavior

### What Syncs

- All variables in the environment
- Changes sync within seconds of saving

### What Doesn't Sync

- Deletions (removing a variable doesn't remove from AWS)
- AWS → 1Password changes (one-way only)

### Secret Format in AWS

Secrets are stored as JSON:

```json
{
    "API_KEY": "actual-api-key-value",
    "DATABASE_URL": "postgres://...",
    "SECRET_TOKEN": "token-value"
}
```

## Limitations

| Limitation | Details |
|------------|---------|
| **Max size** | 64KB per environment |
| **Sync direction** | 1Password → AWS only |
| **Auto-rotation** | Not supported via integration |
| **Deletions** | Must manually delete from AWS |
| **Regions** | One secret per region per environment |

### Recommendations

- Keep 1Password as the single source of truth
- Don't modify the synced secret directly in AWS
- For secrets requiring rotation, keep them AWS-native
- Use separate environments for dev/staging/production

## Accessing Secrets in AWS

### From Lambda

```python
import boto3
import json

def get_secrets():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='1password/my-project/env')
    secrets = json.loads(response['SecretString'])
    return secrets

# Usage
secrets = get_secrets()
api_key = secrets['API_KEY']
```

### From ECS Task Definition

```json
{
    "containerDefinitions": [{
        "secrets": [{
            "name": "API_KEY",
            "valueFrom": "arn:aws:secretsmanager:region:account:secret:1password/my-project/env:API_KEY::"
        }]
    }]
}
```

### From EC2 with IAM Role

```bash
aws secretsmanager get-secret-value \
    --secret-id 1password/my-project/env \
    --query SecretString \
    --output text | jq -r '.API_KEY'
```

## Troubleshooting

### "Access Denied" During Test

**Causes:**
- IAM policy doesn't match secret path
- Role not properly associated with SAML provider
- Missing required permissions

**Solutions:**
1. Verify policy resource matches your secret name pattern
2. Check SAML provider is correctly configured
3. Verify role trust relationship includes the SAML provider

### Sync Not Working

**Causes:**
- Desktop app not running
- Environment not saved
- Network connectivity issues

**Solutions:**
1. Ensure 1Password desktop app is running and unlocked
2. Save changes to the environment
3. Check network connectivity to AWS

### Secret Not Updating

**Causes:**
- Sync delay (usually a few seconds)
- AWS caching
- Integration disabled

**Solutions:**
1. Wait 30 seconds and check again
2. In AWS console, refresh the secret page
3. Verify integration is enabled in 1Password

### KMS Encryption Errors

**Causes:**
- Missing KMS permissions
- Invalid KMS key ARN
- Key in different region

**Solutions:**
1. Add KMS permissions to IAM policy
2. Verify key ARN is correct
3. Ensure KMS key is in same region as secret

## Security Considerations

1. **Least privilege**: Scope IAM policy to specific secret paths
2. **KMS encryption**: Use customer-managed keys for sensitive environments
3. **Audit logging**: Enable CloudTrail for Secrets Manager events
4. **Access review**: Regularly audit who has access to the role
5. **Single source**: Don't edit secrets directly in AWS

## Related Resources

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [1Password Environments Overview](https://developer.1password.com/docs/environments/)
- [AWS IAM Roles for SAML](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_saml.html)
