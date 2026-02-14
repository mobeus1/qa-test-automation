#!/bin/bash
# Fetch application configuration from separate config repository
# Usage: ./fetch-config.sh <app-name> [config-dir]

set -euo pipefail

APP_NAME=${1:?"Error: app_name is required"}
CONFIG_DIR=${2:-"${RUNNER_TEMP:-/tmp}/qa-configs"}
ORG_NAME=${QA_ORG_NAME:-"your-org"}  # Override with env var

CONFIG_REPO="qa-config-${APP_NAME}"
APP_CONFIG_PATH="${CONFIG_DIR}/${APP_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create config cache directory
mkdir -p "${CONFIG_DIR}"

# Check if config already cached (useful for scheduled runs with multiple apps)
if [ -d "${APP_CONFIG_PATH}" ]; then
    log_info "Using cached config for ${APP_NAME}"
    echo "CONFIG_PATH=${APP_CONFIG_PATH}" >> "${GITHUB_OUTPUT:-/dev/stdout}"
    echo "CONFIG_CACHED=true" >> "${GITHUB_OUTPUT:-/dev/stdout}"
    exit 0
fi

log_info "Fetching config for ${APP_NAME} from ${ORG_NAME}/${CONFIG_REPO}"

# Check if GH_TOKEN is set
if [ -z "${GH_TOKEN:-}" ]; then
    log_error "GH_TOKEN environment variable not set"
    exit 1
fi

# Check if repo exists
if ! gh repo view "${ORG_NAME}/${CONFIG_REPO}" &>/dev/null; then
    log_error "Config repository not found: ${ORG_NAME}/${CONFIG_REPO}"
    log_info "Available options:"
    log_info "  1. Create repo: gh repo create ${ORG_NAME}/${CONFIG_REPO}"
    log_info "  2. Check app name spelling"
    log_info "  3. Verify GH_TOKEN has correct permissions"
    exit 1
fi

# Clone config repo with minimal data transfer
log_info "Cloning ${CONFIG_REPO}..."
gh repo clone "${ORG_NAME}/${CONFIG_REPO}" \
    "${APP_CONFIG_PATH}" \
    -- --depth=1 --single-branch --no-tags

# Verify config.json exists
if [ ! -f "${APP_CONFIG_PATH}/config.json" ]; then
    log_error "config.json not found in ${CONFIG_REPO}"
    exit 1
fi

log_info "Successfully fetched config for ${APP_NAME}"
log_info "Config path: ${APP_CONFIG_PATH}"

# Output for GitHub Actions
echo "CONFIG_PATH=${APP_CONFIG_PATH}" >> "${GITHUB_OUTPUT:-/dev/stdout}"
echo "CONFIG_CACHED=false" >> "${GITHUB_OUTPUT:-/dev/stdout}"

# Print config summary
if command -v jq &> /dev/null; then
    log_info "Configuration summary:"
    jq -r '.app_name as $app | 
           .testcomplete.enabled // false as $tc | 
           .jmeter.enabled // false as $jm |
           "  App: \($app)\n  TestComplete: \($tc)\n  JMeter: \($jm)"' \
           "${APP_CONFIG_PATH}/config.json"
fi

exit 0
