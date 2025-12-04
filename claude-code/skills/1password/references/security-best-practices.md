# 1Password Security Best Practices

## Credential Storage

### DO: Use op:// References
```bash
# Safe - can be committed to git
API_KEY=op://Personal/Service/api-key
DATABASE_URL=op://Work/Database/connection-string
```

### DON'T: Store Plaintext Secrets
```bash
# NEVER commit this
API_KEY=sk-1234567890abcdef
DATABASE_URL=postgres://user:password@host:5432/db
```

## File Permissions

### Credentials Directory
```bash
# Create with restricted permissions
mkdir -p ~/.config/mcp-credentials
chmod 700 ~/.config/mcp-credentials
```

### Credentials Files
```bash
# Each .env file should be owner-only
chmod 600 ~/.config/mcp-credentials/*.env
```

### Verify Permissions
```bash
ls -la ~/.config/mcp-credentials/
# Expected: drwx------ (700) for directory
# Expected: -rw------- (600) for files
```

## Vault Organization

### Separation by Sensitivity
```
Personal/           ← Personal accounts, low-risk
├── Social media
├── Shopping sites
└── Personal projects

Work/               ← Work credentials, medium-risk
├── SaaS tools
├── Development APIs
└── Team services

Infrastructure/     ← Production systems, high-risk
├── Cloud providers
├── Database credentials
└── SSH keys
```

### Benefits
- Limit blast radius if compromised
- Easier access control
- Clear audit scope
- Service account scoping

## Service Accounts

### When to Use
- CI/CD pipelines (no biometric available)
- Automated scripts
- Server deployments
- Shared infrastructure

### Best Practices

1. **Least privilege**: Restrict to specific vaults only
   ```bash
   # Service account only accesses CI vault
   op://CI-Secrets/...
   ```

2. **Rotate tokens regularly**: Set calendar reminders

3. **Never commit tokens**:
   ```bash
   # Set in CI/CD secrets, not code
   export OP_SERVICE_ACCOUNT_TOKEN="$CI_SECRET"
   ```

4. **Separate accounts per use case**:
   - One for CI/CD
   - One for production deployments
   - One for monitoring

## Activity Logging

### Enable Logging
1. 1Password → Settings → Developer
2. Enable "Record and display activity"

### What's Logged
- CLI commands executed
- Application that ran the command
- Timestamp
- Success/failure

### Review Regularly
- Check for unexpected access patterns
- Audit before credential rotation
- Monitor for failed attempts

## Developer Watchtower

### Enable
1. 1Password → Settings → Developer
2. Enable "Developer Watchtower"

### What It Detects
- Plaintext secrets on disk
- Weak SSH keys
- Outdated key algorithms
- Unencrypted credential files

### Act on Alerts
- Move detected secrets to 1Password
- Regenerate weak SSH keys
- Update to modern algorithms

## Biometric Security

### Enable Touch ID
- Convenient + secure
- Session-based (times out)
- Requires physical presence

### Timeout Settings
- Shorter timeout = more secure, less convenient
- Default is reasonable for most users
- Adjust in 1Password → Settings → Security

## Never Do List

1. **Never commit plaintext .env files**
   ```bash
   # Add to .gitignore
   .env
   .env.*
   *.env
   !*.env.example  # Example files OK (no real secrets)
   ```

2. **Never share credentials via chat/email**
   - Use 1Password sharing instead
   - Or shared vaults

3. **Never disable biometric permanently**
   - Temporary disable OK for debugging
   - Re-enable immediately after

4. **Never use same credentials across environments**
   - Dev, staging, production should differ
   - Use vault separation

5. **Never store service account tokens in code**
   - Use CI/CD secret management
   - Environment variables at runtime

## Credential Rotation

### Schedule
- API keys: Quarterly minimum
- Passwords: On suspected compromise
- Service account tokens: Quarterly
- SSH keys: Annually or on team changes

### Process
1. Generate new credential in 1Password
2. Update service/application to use new
3. Verify new credential works
4. Delete old credential
5. Log rotation in audit trail

## Emergency Procedures

### Suspected Compromise
1. **Immediately**: Rotate affected credentials
2. **Review**: Activity logs for unauthorized access
3. **Audit**: What systems used those credentials
4. **Update**: All places using old credentials
5. **Document**: Incident for future reference

### Lost Device
1. Sign out all sessions: 1Password.com → Sign Out Everywhere
2. Rotate sensitive credentials
3. Review recent activity
4. Enable additional security if not already

## Backup Considerations

### 1Password Handles Backup
- Encrypted sync to 1Password servers
- No need to backup vault locally

### What YOU Should Backup
- List of which credentials exist (not values)
- Configuration files with op:// references
- Recovery codes stored separately

### What NOT to Backup
- Never export plaintext credentials
- Never copy vault to unencrypted storage
