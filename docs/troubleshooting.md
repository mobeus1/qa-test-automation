# Troubleshooting Guide

## Common Issues

### Dispatch Not Triggering Tests

**Symptom**: You deploy your app but no tests run in the QA repo.

**Checks**:
1. Verify `QA_DISPATCH_PAT` secret is set in your app repo with `repo` scope
2. Confirm the `event-type` matches `deployment-complete`
3. Check the `repository` field points to the correct QA repo
4. Verify the PAT owner has write access to the QA repo
5. Check Actions tab in both repos for failed runs

### TestComplete Runner Not Picking Up Jobs

**Symptom**: Jobs queue indefinitely with "Waiting for a runner".

**Checks**:
1. Verify self-hosted runner is online: Settings > Actions > Runners
2. Confirm runner has labels: `self-hosted`, `windows`, `testcomplete`
3. Check runner machine has TestComplete/TestExecute installed
4. Restart the runner service if needed
5. Check if another job is already running (parallel execution may be disabled)

### TestComplete Tests Failing

**Symptom**: Tests start but fail during execution.

**Checks**:
1. Verify `TEST_EXECUTE_ACCESS_KEY` secret is valid and not expired
2. Check app config at `configs/apps/{app}/testcomplete.json` has correct project_suite path
3. Verify the test_items list matches actual test names in the project
4. Check if the target environment (base_url) is accessible from the runner
5. Review test artifacts uploaded to the Actions run for screenshots and logs

### Config File Not Found

**Symptom**: Error "Config not found: configs/apps/{app}/testcomplete.json"

**Checks**:
1. Verify the `app-name` in the dispatch payload matches the folder name exactly
2. Check the config file exists at the expected path
3. Ensure the JSON is valid (no trailing commas, proper quoting)

### JMeter Health Checks Failing

**Symptom**: JMeter tests report failures or threshold violations.

**Checks**:
1. Verify endpoints in `configs/apps/{app}/jmeter.json` are correct and accessible
2. Check if the target environment is up and healthy
3. Review thresholds - they may be too strict for your environment:
   - `max_response_time_ms`: Maximum acceptable response time
   - `max_error_rate_percent`: Maximum acceptable error rate
   - `p90_response_time_ms` / `p95_response_time_ms`: Percentile thresholds
4. Check the JMeter HTML report artifact for detailed breakdown
5. Verify the base_url for the environment is correct

### JMeter Installation Failures

**Symptom**: JMeter workflow fails at setup step.

**Checks**:
1. JMeter is downloaded from Apache mirrors - check if the version (5.6.3) is still available
2. Verify Java 17 setup succeeded
3. Check for network connectivity issues on the runner
4. Review `configs/shared-settings.json` for correct JMeter version setting

### JMeter Test Plan Not Found

**Symptom**: Error about missing .jmx test plan file.

**Checks**:
1. If using custom .jmx plans, verify they exist at `test-suites/{app}/jmeter/`
2. If relying on auto-generated plans, ensure `health_endpoints` is configured in jmeter.json
3. Verify the `test-plan` input matches a key in your config's `test_plans` section

### Notification Failures

**Symptom**: Tests run but no Slack/email notifications sent.

**Checks**:
1. Verify `NOTIFICATION_WEBHOOK` secret is set and valid
2. Check if notifications are configured for the event type (failure vs success)
3. Test the webhook URL manually with a curl command
4. Review the notify step logs in the Actions run

### Scheduled Regression Not Running

**Symptom**: Cron jobs don't trigger on schedule.

**Checks**:
1. GitHub Actions cron may have up to 15-minute delay
2. Scheduled workflows only run on the default branch (main)
3. Repos with no activity for 60+ days may have Actions disabled
4. Verify cron syntax is correct in `scheduled-regression.yml`

## Getting Help

1. Check the Actions tab for detailed error logs
2. Review test artifacts (screenshots, HTML reports) uploaded per run
3. Consult the [Architecture Guide](architecture.md) for system design context
4. Contact the QA team via #qa-automation Slack channel
