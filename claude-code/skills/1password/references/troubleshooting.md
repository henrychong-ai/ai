# 1Password CLI Troubleshooting

## Common Errors and Solutions

### "Unexpected response from 1Password app"

**Cause:** 1Password is locked or not running.

**Solution:**
1. Open 1Password app
2. Unlock with password or biometric
3. Retry the command

**Verification:**
```bash
op vault list  # Should work without error
```

---

### "Could not find item"

**Cause:** Item name, vault, or field doesn't match.

**Solutions:**

1. **List items in vault:**
   ```bash
   op item list --vault="VaultName"
   ```

2. **Check exact item name:**
   ```bash
   op item get "ItemName" --vault="VaultName"
   ```

3. **View available fields:**
   ```bash
   op item get "ItemName" --vault="VaultName" --format=json | jq '.fields[].label'
   ```

4. **Correct the reference:**
   ```bash
   # Wrong
   op://Personal/Github/token

   # Correct (check capitalization)
   op://Personal/GitHub/api-token
   ```

---

### "Authentication required" / Touch ID Not Appearing

**Cause:** CLI integration not enabled or biometric timeout.

**Solutions:**

1. **Enable CLI integration:**
   - 1Password → Settings → Developer
   - Enable "Integrate with 1Password CLI"

2. **Enable Touch ID:**
   - 1Password → Settings → Security
   - Enable Touch ID

3. **Check background permissions:**
   - System Settings → Login Items
   - Ensure 1Password is allowed in background

4. **Re-authenticate:**
   ```bash
   op signin
   ```

---

### "Connection reset by peer"

**Cause:** 1Password background process not running.

**Solutions:**

1. **Allow in background:**
   - System Settings → General → Login Items
   - Find 1Password, enable "Allow in background"

2. **Restart 1Password:**
   - Quit 1Password completely
   - Reopen the app
   - Unlock

3. **Check process:**
   ```bash
   pgrep -l 1Password
   ```

---

### MCP Server Won't Start

**Diagnosis steps:**

1. **Is 1Password unlocked?**
   ```bash
   op vault list
   ```

2. **Does credentials file exist?**
   ```bash
   cat ~/.config/mcp-credentials/server-name.env
   ```

3. **Test op run manually:**
   ```bash
   op run --env-file=~/.config/mcp-credentials/server-name.env -- env | head
   ```

4. **Test the MCP command directly:**
   ```bash
   op run --env-file=~/.config/mcp-credentials/server-name.env -- npx mcp-server-name
   ```

**Recovery:**
```bash
# In Claude Code
/mcp restart server-name

# Or restart Claude Code entirely
```

---

### MCP Server Fails After 1Password Unlock

**Cause:** Claude Code doesn't auto-retry failed MCP servers.

**Solution:**
1. Unlock 1Password
2. Either:
   - `/mcp restart server-name` in Claude Code
   - Restart Claude Code application

---

### Slow op run Startup

**Cause:** Many secrets to fetch, or network latency.

**Solutions:**

1. **Consolidate secrets:**
   - Fewer items = fewer fetches
   - Store related secrets in one item

2. **Check network:**
   - 1Password fetches from servers
   - Slow network = slow fetches

3. **Use service account with caching:**
   - Service accounts can cache locally
   - Better for CI/CD environments

---

### "Invalid session" or "Session expired"

**Cause:** 1Password session timed out.

**Solutions:**

1. **Re-authenticate:**
   ```bash
   op signin
   ```

2. **Check biometric is working:**
   - Try unlocking 1Password app directly
   - Then retry CLI command

---

### Service Account Not Working

**Cause:** Token issues or vault permissions.

**Solutions:**

1. **Verify token is set:**
   ```bash
   echo $OP_SERVICE_ACCOUNT_TOKEN | head -c 20
   # Should show: ops_xxxx...
   ```

2. **Check vault access:**
   - Service accounts have limited vault access
   - Verify the vault is shared with the service account

3. **Test with account list:**
   ```bash
   op account list
   # Should show service account
   ```

---

### "Permission denied" on Wrapper Script

**Cause:** Script not executable.

**Solution:**
```bash
chmod +x ~/.config/1password/op-mcp-wrapper
ls -la ~/.config/1password/op-mcp-wrapper
# Should show: -rwx------
```

---

### Environment Variables Not Injected

**Cause:** op:// reference syntax error.

**Check:**
1. Reference format: `op://vault/item/field`
2. No quotes around reference in .env file
3. No spaces around `=`

**Correct:**
```bash
API_KEY=op://Personal/Service/key
```

**Incorrect:**
```bash
API_KEY="op://Personal/Service/key"  # Don't quote
API_KEY = op://Personal/Service/key  # No spaces
```

---

## Diagnostic Commands

### Check 1Password CLI Status
```bash
# Version
op --version

# Connected accounts
op account list

# Current session
op whoami

# List vaults
op vault list
```

### Test Secret Access
```bash
# Read single secret
op read "op://Personal/Test/password"

# List items
op item list --vault="Personal"

# Get item details
op item get "ItemName" --vault="Personal"
```

### Test op run
```bash
# Test with echo
op run --env-file=test.env -- sh -c 'echo $SECRET_VAR'

# Test with env
op run --env-file=test.env -- env | grep SECRET
```

### Check System Integration
```bash
# 1Password processes
pgrep -la 1Password

# CLI location
which op

# Check PATH includes op
echo $PATH | tr ':' '\n' | grep -E "(homebrew|1password)"
```

## GitHub Actions Issues

### Secrets Not Loading in Workflow

**Diagnosis:**
1. Check service account token is stored in GitHub secrets
2. Verify vault access for service account
3. Check runner type (Windows not supported)

**Solutions:**
1. Store `OP_SERVICE_ACCOUNT_TOKEN` in repository secrets
2. Grant vault access to service account in 1Password.com
3. Use `ubuntu-latest` or `macos-latest` runner

---

### "Cannot create item in piped environment"

**Cause:** Direct CLI input via pipe not supported in CI.

**Solution:** Use JSON template with piped input:
```bash
echo '{"title":"Item","category":"LOGIN","fields":[...]}' | op item create --template=-
```

---

### Secrets Visible in Logs

**Cause:** Secret used before masking or in unexpected format.

**Solution:** The `load-secrets-action` automatically masks secrets. If still visible:
1. Don't echo secrets directly
2. Use `::add-mask::` for custom secrets
3. Check secret isn't split across multiple lines

See `github-actions-guide.md` for complete CI/CD troubleshooting.

---

## AWS Secrets Manager Sync Issues

### "Access Denied" During Setup

**Causes:**
- IAM policy doesn't match secret path
- SAML provider misconfigured
- Role trust relationship incorrect

**Solutions:**
1. Verify IAM policy resource matches `arn:aws:secretsmanager:*:*:secret:1password/*`
2. Re-download and re-upload SAML metadata
3. Check role trust includes the SAML provider ARN

See `aws-secrets-manager.md` for detailed setup and troubleshooting.

---

## Getting Help

### 1Password Support
- https://support.1password.com
- https://1password.community

### Developer Documentation
- https://developer.1password.com/docs/cli/

### Common Log Locations
- 1Password app: Built-in activity log
- CLI: `op --debug command` for verbose output
