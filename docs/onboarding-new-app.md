# Onboarding a New Application

This guide walks through adding a new application to the centralized QA test automation system.

## Prerequisites

- Access to this repository (qa-test-automation)
- A GitHub PAT with `repo` scope for cross-repo dispatch
- Your application's test suites ready in TestComplete and/or JMeter

## Step 1: Create Application Config Folder

Create a new folder under `configs/apps/` with your application name:

```
configs/apps/{your-app-name}/
  testcomplete.json
  jmeter.json
  CODEOWNERS
```

## Step 2: Configure TestComplete

Create `configs/apps/{your-app-name}/testcomplete.json` using `configs/apps/member-portal/testcomplete.json` as a template. Key fields to customize:

- `app_name`: Your unique application identifier
- `project_suite`: Path to your .pjs TestComplete project
- `test_items`: Define SmokeTests, RegressionTests, and FullRegression suites
- `environments`: Set staging and production URLs and credential secret names

## Step 3: Configure JMeter Health Checks

Create `configs/apps/{your-app-name}/jmeter.json` using `configs/apps/member-portal/jmeter.json` as a template. Key fields:

- `health_endpoints`: API endpoints to monitor (e.g., /api/health, /api/status)
- `test_plans`: Define health-check, smoke, load, stress plans with thread counts
- `thresholds`: Set max response time and error rate limits
- `environments`: Base URLs per environment

## Step 4: Set Up CODEOWNERS

Create `configs/apps/{your-app-name}/CODEOWNERS` to assign team ownership.

## Step 5: Add Test Suites

Place your test project files under `test-suites/{your-app-name}/`:

```
test-suites/{your-app-name}/
  testcomplete/    # TestComplete .pjs project
  jmeter/          # Custom JMeter .jmx plans (optional)
```

Note: If you don't provide custom .jmx files, the system auto-generates health check plans from your health_endpoints config.

## Step 6: Add GitHub Secrets

Add per-app secrets to the qa-test-automation repository:
- `{APP}_STAGING_CREDS` - Staging credentials
- `{APP}_PROD_CREDS` - Production credentials

## Step 7: Add Dispatch Trigger to Your App Repo

Copy `.github/workflows/dispatch-example.yml` to your app repository and customize the app_name, test_suite, and test_type fields.

Add `QA_DISPATCH_PAT` secret to your app repo.

## Step 8: Add to Scheduled Regression

Update `.github/workflows/scheduled-regression.yml` to include your app in both TestComplete and JMeter scheduled runs.

## Step 9: Update Root CODEOWNERS

Add your app's config path to `.github/CODEOWNERS`.

## Verification Checklist

- [ ] Config files created and valid JSON
- [ ] CODEOWNERS set up for your team
- [ ] Test suites placed in correct directory
- [ ] GitHub secrets configured
- [ ] Dispatch trigger added to app repo
- [ ] Scheduled regression updated
- [ ] Manual workflow_dispatch test successful
- [ ] Post-deploy dispatch test successful
