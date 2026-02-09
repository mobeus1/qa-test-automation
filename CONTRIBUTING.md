# Contributing to QA Test Automation Hub

Thank you for your interest in contributing to the QA Test Automation Hub! This guide will help you get started.

## Getting Started

### Prerequisites

- GitHub account with access to this repository
- Understanding of GitHub Actions workflows
- Familiarity with SmartBear TestComplete/TestExecute
- Python 3.8+ (for helper scripts)

### Repository Setup

1. Clone the repository
2. Review the architecture documentation in docs/architecture.md
3. Understand the workflow structure in .github/workflows/

## How to Contribute

### Adding a New Application

This is the most common contribution. Follow the onboarding guide at docs/onboarding-new-app.md.

Quick steps:
1. Create a config file in configs/your-app.json
2. Add your TestComplete project suite to test-suites/your-app/
3. Add the dispatch workflow to your application repository
4. Update scheduled-regression.yml to include your app
5. Test the integration

### Modifying Workflows

When modifying GitHub Actions workflows:
- Test changes in a feature branch first
- Use workflow_dispatch for manual testing
- Ensure backward compatibility with existing app configs
- Update documentation if inputs/outputs change

### Updating Scripts

For changes to helper scripts (scripts/):
- Maintain backward compatibility
- Add error handling for edge cases
- Test with multiple app configurations
- Update inline documentation

### Documentation Changes

- Keep docs accurate and up-to-date
- Use clear, concise language
- Include examples where helpful
- Update the table of contents if adding sections

## Code Standards

### YAML Workflows
- Use consistent indentation (2 spaces)
- Add descriptive step names
- Include comments for non-obvious logic
- Use GitHub Actions best practices

### Python Scripts
- Follow PEP 8 style guide
- Add docstrings to functions
- Use type hints where applicable
- Handle errors gracefully

### JSON Configurations
- Use consistent formatting (2 space indent)
- Include all required fields
- Add descriptive values for documentation

## Pull Request Process

1. Create a feature branch from main
2. Make your changes
3. Test thoroughly
4. Submit a pull request with:
   - Clear description of changes
   - Testing performed
   - Impact on existing apps
5. Request review from QA team
6. Address review feedback
7. Merge after approval

## Reporting Issues

When reporting issues:
- Use the GitHub issue tracker
- Include steps to reproduce
- Attach relevant logs or screenshots
- Specify which app/workflow is affected

## Questions?

- Check the troubleshooting guide: docs/troubleshooting.md
- Open a GitHub issue for questions
- Contact the QA team

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
