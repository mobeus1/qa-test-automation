# Troubleshooting Guide

Common issues and solutions for the QA Test Automation Hub.

## Dispatch Issues

### Tests don't trigger after deployment

**Symptoms**: Deployment completes in your app repo but no test run appears in qa-test-automation.

**Solutions**:
1. Verify QA_DISPATCH_PAT secret is set in your app repo with repo scope
2. Check the dispatch workflow exists at .github/workflows/trigger-qa-tests.yml
3. Ensure event_type is exactly "deployment-complete"
4. Verify the PAT hasn't expired
5. Check the app repo Actions tab for dispatch workflow failures

### Invalid payload error

**Symptoms**: Orchestrator fails at the "Validate Payload" step.

**Solutions**:
1. Ensure app_name matches a config file in configs/ (without .json extension)
2. Environment must be "staging" or "production"
3. Check client_payload JSON formatting in your dispatch workflow

## Runner Issues

### "No runner found" error

**Symptoms**: Workflow queued but never starts.

**Solutions**:
1. Verify a self-hosted runner with labels [self-hosted, windows, testcomplete] is online
2. Check runner status at Settings > Actions > Runners
3. Restart the runner service on the Windows machine
4. Ensure the runner has TestComplete/TestExecute installed

### TestComplete/TestExecute not found

**Symptoms**: run-tests.bat fails with "Neither TestExecute nor TestComplete found"

**Solutions**:
1. Verify installation path: C:\Program Files (x86)\SmartBear\TestComplete 15\
2. Or: C:\Program Files (x86)\SmartBear\TestExecute 15\
3. Check that the installation isn't corrupted
4. Ensure proper licensing is configured

### Tests timeout

**Symptoms**: Workflow cancelled after timeout period.

**Solutions**:
1. Increase timeout_minutes in your app config JSON
2. Check if the application under test is responding
3. Look for hung browser processes on the runner
4. Review TestComplete logs for stuck tests

## Configuration Issues

### Config file not found

**Symptoms**: "Load Application Config" step fails.

**Solutions**:
1. Config filename must match the app-name input exactly
2. File must be in configs/ directory with .json extension
3. Verify JSON syntax is valid

### Environment URL incorrect

**Symptoms**: Tests run but fail to connect to the application.

**Solutions**:
1. Verify base_url in your config matches the actual deployment URL
2. Check if the environment is accessible from the runner machine
3. Ensure SSL certificates are valid (no self-signed cert issues)

## Test Execution Issues

### Tests pass locally but fail in CI

**Solutions**:
1. Screen resolution: Ensure runner has adequate screen resolution
2. Browser cache: Tests may need a clean browser state
3. Timing: Add appropriate waits for CI environment
4. Network: Verify runner can access all test dependencies
5. Credentials: Check environment-specific credentials

### Flaky tests

**Solutions**:
1. Enable retry_on_failure in your app config
2. Add explicit waits instead of fixed sleep times
3. Isolate tests to avoid dependencies between them
4. Check for timing-sensitive assertions

### Missing test artifacts

**Symptoms**: Workflow completes but no artifacts are uploaded.

**Solutions**:
1. Verify test-results/ directory exists after execution
2. Check log output for file path issues
3. Ensure artifact upload step has if: always() condition
4. Check artifact size limits (GitHub has a 500MB limit)

## Notification Issues

### No Slack notifications on failure

**Solutions**:
1. Verify NOTIFICATION_WEBHOOK secret is set
2. Check webhook URL is valid and active
3. Look for errors in the notification step logs
4. Verify the Slack app/integration is properly configured

## Workflow Issues

### Reusable workflow not found

**Symptoms**: Error referencing ./.github/workflows/run-testcomplete.yml

**Solutions**:
1. The file must exist on the default branch (main)
2. Filename must match exactly (case-sensitive)
3. Ensure the file has workflow_call trigger defined

### Secrets not available in reusable workflow

**Solutions**:
1. Secrets must be explicitly passed in the uses: section
2. Check secret names match between caller and callee
3. Verify secrets are set at the repository level

## Getting More Help

1. Check GitHub Actions workflow logs for detailed error messages
2. Review the architecture docs at docs/architecture.md
3. Open an issue in this repository
4. Contact the QA team

## Useful Commands

```bash
# Check workflow runs
gh run list --repo mobeus1/qa-test-automation

# View specific run logs
gh run view <run-id> --repo mobeus1/qa-test-automation --log

# Manually trigger tests
gh workflow run run-testcomplete.yml -f app-name=app-a -f environment=staging

# Test dispatch payload
gh api repos/mobeus1/qa-test-automation/dispatches \
  -f event_type=deployment-complete \
  -f 'client_payload[app_name]=app-a' \
  -f 'client_payload[environment]=staging'
```
