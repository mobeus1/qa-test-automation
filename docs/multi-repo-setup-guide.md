# Quick Setup Guide: Multi-Repo Config

This guide helps you create and configure your application's QA config repository.

## Option 1: Automated Setup (Recommended)

Use the migration script to automatically create your config repo:

```bash
# Run from the qa-test-automation directory
python scripts/migrate-to-multi-repo.py \
  --org your-org \
  --apps your-app-name

# Or dry-run first to see what would happen
python scripts/migrate-to-multi-repo.py \
  --org your-org \
  --apps your-app-name \
  --dry-run
```

## Option 2: Manual Setup

### Step 1: Create Repository

```bash
# Create new private repo
gh repo create your-org/qa-config-your-app-name --private

# Clone it
gh repo clone your-org/qa-config-your-app-name
cd qa-config-your-app-name
```

### Step 2: Copy Config Template

```bash
# Copy the template
cp /path/to/qa-test-automation/examples/config-template.json config.json

# Replace placeholders
sed -i 's/{{APP_NAME}}/your-app-name/g' config.json
sed -i 's/{{APP_NAME_UPPER}}/YOUR_APP_NAME/g' config.json
sed -i 's/{{TEAM_NAME}}/Your Team Name/g' config.json
sed -i 's/{{TEAM_LEAD}}/team-lead-handle/g' config.json
```

### Step 3: Add Test Suites

```bash
# Create directories
mkdir -p testcomplete jmeter

# Copy your TestComplete project
cp -r /path/to/your/testcomplete/project/* testcomplete/

# (Optional) Copy custom JMeter plans
cp /path/to/your/jmeter/*.jmx jmeter/
```

### Step 4: Create CODEOWNERS

```bash
cat > CODEOWNERS <<EOF
# QA Config Owners
* @your-org/your-team-name
config.json @your-org/qa-team
EOF
```

### Step 5: Create README

```bash
cat > README.md <<EOF
# QA Test Configuration - Your App Name

This repository contains test configuration and test suites for **Your App Name**.

## Structure

- \`config.json\` - Combined TestComplete and JMeter configuration
- \`testcomplete/\` - TestComplete test project
- \`jmeter/\` - JMeter test plans
- \`CODEOWNERS\` - Team ownership

## Quick Links

- [Application Repository](https://github.com/your-org/your-app-name)
- [QA Orchestrator](https://github.com/your-org/qa-test-automation)
- [Test Documentation](https://docs.example.com/testing/your-app-name)

## Running Tests

Tests are automatically triggered by the [QA orchestrator](https://github.com/your-org/qa-test-automation) when:
- Your app deploys (via repository_dispatch)
- Scheduled regression runs execute
- Manual workflow_dispatch is triggered

## Updating Configuration

1. Edit \`config.json\` with your changes
2. Validate against schema: \`gh repo clone your-org/qa-test-automation && ajv validate -s qa-test-automation/examples/config-schema.json -d config.json\`
3. Commit and push
4. Next test run will use updated config

## Support

- Team: @your-team
- Contact: your-team@example.com
- Slack: #qa-your-app
EOF
```

### Step 6: Validate Configuration

```bash
# Install ajv-cli if not already installed
npm install -g ajv-cli

# Validate your config against schema
gh repo clone your-org/qa-test-automation /tmp/qa-automation
ajv validate \
  -s /tmp/qa-automation/examples/config-schema.json \
  -d config.json
```

### Step 7: Commit and Push

```bash
git add .
git commit -m "Initial QA configuration for your-app-name"
git push -u origin main
```

### Step 8: Add GitHub Topics

```bash
gh repo edit your-org/qa-config-your-app-name \
  --add-topic qa-automation \
  --add-topic qa-config \
  --add-topic test-configuration
```

### Step 9: Set Up Secrets

Add any required secrets to the **central qa-test-automation repo**:

```bash
# Example: Add staging credentials
gh secret set YOUR_APP_NAME_STAGING_CREDS \
  --repo your-org/qa-test-automation \
  --body "username:password"

# Example: Add production credentials
gh secret set YOUR_APP_NAME_PROD_CREDS \
  --repo your-org/qa-test-automation \
  --body "username:password"
```

### Step 10: Test Integration

Trigger a test run manually to verify everything works:

```bash
# Trigger via GitHub Actions UI
gh workflow run orchestrator.yml \
  --repo your-org/qa-test-automation \
  -f app_name=your-app-name \
  -f environment=staging \
  -f test_suite=SmokeTests \
  -f test_type=all
```

## Maintenance

### Updating Test Suites

```bash
# Update TestComplete project
cd testcomplete
# Make your changes
git add .
git commit -m "Update test cases for new feature"
git push
```

### Updating Configuration

```bash
# Edit config
vim config.json

# Validate
ajv validate -s ../qa-test-automation/examples/config-schema.json -d config.json

# Commit
git add config.json
git commit -m "Update performance thresholds"
git push
```

### Version Control

Tag important configuration milestones:

```bash
git tag -a v1.0.0 -m "Baseline configuration"
git push origin v1.0.0
```

## Troubleshooting

### Config Not Found Error

If orchestrator can't find your config:

1. Verify repo name matches pattern: `qa-config-{app-name}`
2. Check `app_name` in config.json matches the dispatched value
3. Verify GH_TOKEN has access to your config repo

### Test Suites Not Loading

1. Check paths in config.json match actual file locations
2. Verify files are committed and pushed
3. Check file permissions and .gitignore

### Schema Validation Fails

```bash
# Get detailed validation errors
ajv validate \
  -s ../qa-test-automation/examples/config-schema.json \
  -d config.json \
  --errors=text
```

## Best Practices

1. **Keep configs small**: Only include what's necessary
2. **Use environment variables**: Don't hardcode secrets
3. **Version your configs**: Tag releases that match app versions
4. **Document changes**: Write descriptive commit messages
5. **Test locally**: Validate schema before pushing
6. **Review changes**: Use PRs even for config repos
7. **Monitor test runs**: Check orchestrator execution logs

## Getting Help

- **Documentation**: [qa-test-automation/docs](https://github.com/your-org/qa-test-automation/tree/main/docs)
- **Issues**: [Report a problem](https://github.com/your-org/qa-test-automation/issues)
- **Slack**: #qa-automation
- **Email**: qa-team@example.com
