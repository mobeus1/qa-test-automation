# Architecture Guide

## Overview

The QA Test Automation Hub uses a **hub-and-spoke architecture** to centralize test orchestration while allowing individual application teams to maintain ownership of their deployment pipelines.

## Design Principles

1. **Separation of Concerns**: Test logic lives in the hub; deployment logic lives in app repos
2. **Configuration over Code**: Apps are onboarded via JSON config, not workflow changes
3. **Reusability**: A single reusable workflow serves all applications
4. **Observability**: Every run produces artifacts, summaries, and notifications
5. **Scalability**: Adding a new app requires only a config file and dispatch trigger

## Component Architecture

### Hub Components

#### Reusable Workflow (run-testcomplete.yml)
The core execution engine. Accepts standardized inputs (app-name, environment, test-suite) and handles the full lifecycle: config loading, test execution, result parsing, artifact upload, and notifications. All other workflows delegate to this one.

#### Orchestrator (orchestrator.yml)
Listens for repository_dispatch events from application repositories. Validates the payload, extracts parameters, and delegates to the reusable workflow. Acts as the entry point for automated post-deployment testing.

#### Scheduled Regression (scheduled-regression.yml)
Cron-triggered workflow that runs regression tests on a schedule. Weeknights run standard regression; Saturday runs full regression. Each app gets its own parallel job for independent execution.

#### Dispatch Example (dispatch-example.yml)
Template workflow for app repos. Teams copy this to their repository and customize it to trigger QA tests after their deployment completes.

### Configuration Layer

#### Application Configs (configs/*.json)
Each app has a JSON config defining its TestComplete project, test suites, environment URLs, credentials, timeouts, and notification preferences. The reusable workflow reads this at runtime.

#### Shared Settings (configs/shared-settings.json)
Global defaults for TestComplete settings, runner labels, artifact retention, and notification channels.

### Execution Layer

#### TestComplete Runner (scripts/run-tests.bat)
Windows batch script that wraps the TestComplete/TestExecute CLI. Handles tool detection, test execution, log export, and exit code mapping.

#### Result Parser (scripts/parse-results.py)
Processes TestComplete output into structured JSON summaries for GitHub Actions job summaries and downstream consumers.

#### Notification Handler (scripts/notify.py)
Sends Slack-compatible webhook notifications with test status, app info, and links to the GitHub Actions run.

## Workflow Patterns

### Pattern 1: Post-Deployment (Automated)

```
App Repo deploys -> workflow_run triggers dispatch workflow
  -> repository_dispatch to qa-test-automation
    -> orchestrator validates payload
      -> reusable workflow executes tests
        -> results uploaded, notifications sent
```

Best for: Continuous integration, smoke tests after every deployment.

### Pattern 2: Scheduled Regression

```
Cron trigger fires -> determine test suite based on day
  -> parallel jobs for each app
    -> reusable workflow executes tests
      -> summary job aggregates results
```

Best for: Nightly regression, weekend full regression, compliance testing.

### Pattern 3: Manual Dispatch

```
User triggers via UI or CLI -> workflow_dispatch
  -> reusable workflow executes tests
    -> results uploaded
```

Best for: Ad-hoc testing, debugging, pre-release validation.

## Security Model

### Secrets Management
- TEST_EXECUTE_ACCESS_KEY: Stored at repo level, passed to reusable workflow
- App credentials: Stored as separate secrets per app/environment
- QA_DISPATCH_PAT: Stored in app repos, used only for cross-repo dispatch
- NOTIFICATION_WEBHOOK: Optional, stored at repo level

### Access Control
- CODEOWNERS enforces QA team review for all changes
- Branch protection on main prevents direct pushes
- Fine-grained PATs scoped to minimum required permissions

## Scaling Considerations

### Adding More Apps
The architecture scales linearly. Each new app requires:
- One config file (no workflow changes for dispatch/manual)
- One job added to scheduled-regression.yml
- Runner capacity for parallel execution

### Runner Capacity
- Self-hosted runners on Windows machines with TestComplete
- max_parallel_suites in shared-settings.json controls concurrency
- Add more runners for horizontal scaling
- Consider runner groups for environment isolation

### Performance
- Apps run in parallel during scheduled regression
- Independent failures don't block other apps
- Artifact upload happens per-app for isolation
- Timeout per-app prevents runaway tests

## Decision Matrix

| Scenario | Trigger | Suite | Environment |
|----------|---------|-------|-------------|
| After staging deploy | repository_dispatch | SmokeTests | staging |
| After prod deploy | repository_dispatch | SmokeTests | production |
| Nightly (weekday) | schedule | RegressionTests | staging |
| Weekend | schedule | FullRegression | staging |
| Pre-release check | workflow_dispatch | FullRegression | staging |
| Debugging | workflow_dispatch | SmokeTests | any |

## Future Considerations

- **Test Parallelization**: Split large suites across multiple runners
- **Result Dashboard**: Aggregate historical results for trend analysis
- **Dynamic Config**: Pull configs from a central config service
- **Cross-Browser**: Extend to run same tests across multiple browsers
- **API Testing**: Add non-TestComplete test runners for API tests
