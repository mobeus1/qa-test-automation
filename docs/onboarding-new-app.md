# Onboarding a New Application

This guide walks you through adding a new application to the QA Test Automation Hub.

## Prerequisites

Before you begin, ensure you have:
- A TestComplete project suite for your application
- A GitHub Personal Access Token (PAT) with repo scope
- Access to this qa-test-automation repository
- Access to your application's GitHub repository

## Step 1: Create Application Configuration

Create a new JSON configuration file in the configs/ directory.

File: configs/your-app.json

```json
{
  "app_name": "your-app",
  "description": "Your Application Description",
  "project_suite": "test-suites/your-app/YourApp.pjs",
  "test_items": {
    "SmokeTests": ["Login", "BasicNavigation"],
    "RegressionTests": ["Login", "BasicNavigation", "AdvancedFeatures"],
    "FullRegression": ["Login", "BasicNavigation", "AdvancedFeatures", "EdgeCases"]
  },
  "environments": {
    "staging": {
      "base_url": "https://staging.your-app.com",
      "credentials_secret": "YOUR_APP_STAGING_CREDS"
    },
    "production": {
      "base_url": "https://your-app.com",
      "credentials_secret": "YOUR_APP_PROD_CREDS"
    }
  },
  "timeout_minutes": 30,
  "notifications": {
    "on_failure": ["your-team@example.com"],
    "on_success": []
  },
  "tags": ["web"]
}
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| app_name | Yes | Unique identifier matching the config filename |
| description | No | Human-readable description |
| project_suite | Yes | Path to TestComplete .pjs file |
| test_items | Yes | Map of suite names to test item arrays |
| environments | Yes | Per-environment URLs and credential secrets |
| timeout_minutes | No | Max execution time (default: 30) |
| notifications | No | Email addresses for notifications |
| tags | No | Categorization tags |

## Step 2: Add TestComplete Project Suite

Place your TestComplete project files under test-suites/your-app/:

```
test-suites/
  your-app/
    YourApp.pjs          # Project suite file
    YourApp.mds          # Master data storage
    Script/              # Test scripts
    Stores/              # Object repositories
```

## Step 3: Add Dispatch Workflow to Your App Repository

Copy the dispatch example workflow to your application repository:

Source: .github/workflows/dispatch-example.yml
Destination: your-app-repo/.github/workflows/trigger-qa-tests.yml

Update the following in the copied file:
- Replace "your-app-name" with your actual app name
- Verify the deployment workflow name matches yours
- Ensure environment detection logic is correct

## Step 4: Configure Secrets

### In Your Application Repository

Add the following secret:
- QA_DISPATCH_PAT: A GitHub PAT with repo scope that can trigger workflows in the qa-test-automation repository

### In the QA Repository (if not already set)

Ensure these secrets exist:
- TEST_EXECUTE_ACCESS_KEY: SmartBear TestExecute access key
- NOTIFICATION_WEBHOOK: Slack/Teams webhook URL (optional)
- YOUR_APP_STAGING_CREDS: App-specific credentials (if needed)

## Step 5: Add to Scheduled Regression

Edit .github/workflows/scheduled-regression.yml and add a new job:

```yaml
  run-your-app:
    needs: determine-suite
    uses: ./.github/workflows/run-testcomplete.yml
    with:
      app-name: your-app
      environment: staging
      test-suite: ${{ needs.determine-suite.outputs.test-suite }}
    secrets:
      TEST_EXECUTE_ACCESS_KEY: ${{ secrets.TEST_EXECUTE_ACCESS_KEY }}
      NOTIFICATION_WEBHOOK: ${{ secrets.NOTIFICATION_WEBHOOK }}
```

Also update the summary job to include your app.

## Step 6: Test the Integration

### Manual Test via CLI

```bash
gh api repos/mobeus1/qa-test-automation/dispatches \
  -f event_type=deployment-complete \
  -f 'client_payload[app_name]=your-app' \
  -f 'client_payload[environment]=staging' \
  -f 'client_payload[version]=test-v1.0'
```

### Manual Test via GitHub UI

1. Go to Actions tab in qa-test-automation
2. Select "Run TestComplete Tests"
3. Click "Run workflow"
4. Enter your app name and environment
5. Monitor the run

### Verify End-to-End

1. Trigger a deployment in your app repository
2. Verify the dispatch workflow runs
3. Confirm tests execute in qa-test-automation
4. Check test results and artifacts

## Troubleshooting

If tests don't trigger, check:
- PAT has correct permissions
- App name matches config filename exactly
- Dispatch event type is "deployment-complete"
- Workflow file is in the correct location

See docs/troubleshooting.md for more help.
