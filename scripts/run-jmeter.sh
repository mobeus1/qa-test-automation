#!/bin/bash
# ============================================================
# JMeter Health Check Runner
# Usage: run-jmeter.sh --app <name> --base-url <url> --endpoints <csv>
#        --test-plan <plan> --threads <n> --duration <s> --output-dir <dir>
# ============================================================

set -euo pipefail

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --app) APP_NAME="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --endpoints) ENDPOINTS="$2"; shift 2 ;;
    --test-plan) TEST_PLAN="$2"; shift 2 ;;
    --threads) THREADS="$2"; shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Defaults
THREADS=${THREADS:-1}
DURATION=${DURATION:-60}
OUTPUT_DIR=${OUTPUT_DIR:-test-results/jmeter}
TEST_PLAN=${TEST_PLAN:-health-check}

echo "============================================================"
echo "QA Test Automation - JMeter Health Check Runner"
echo "============================================================"
echo "Application: $APP_NAME"
echo "Base URL:    $BASE_URL"
echo "Endpoints:   $ENDPOINTS"
echo "Test Plan:   $TEST_PLAN"
echo "Threads:     $THREADS"
echo "Duration:    ${DURATION}s"
echo "Output:      $OUTPUT_DIR"
echo "============================================================"

mkdir -p "$OUTPUT_DIR"

# Determine JMeter test plan file
JMX_FILE="test-suites/$APP_NAME/jmeter/${TEST_PLAN}.jmx"

if [ ! -f "$JMX_FILE" ]; then
  echo "JMX file not found: $JMX_FILE"
  echo "Generating dynamic health check plan..."
  JMX_FILE="$OUTPUT_DIR/dynamic-health-check.jmx"

  # Generate a dynamic JMeter test plan for health checks
  IFS=',' read -ra ENDPOINT_ARRAY <<< "$ENDPOINTS"

  cat > "$JMX_FILE" << 'JMXEOF'
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Health Check Plan">
      <boolProp name="TestPlan.functional_mode">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Health Check Threads">
        <intProp name="ThreadGroup.num_threads">THREADS_PLACEHOLDER</intProp>
        <intProp name="ThreadGroup.ramp_time">5</intProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">DURATION_PLACEHOLDER</stringProp>
      </ThreadGroup>
      <hashTree>
JMXEOF

  for endpoint in "${ENDPOINT_ARRAY[@]}"; do
    endpoint=$(echo "$endpoint" | xargs)  # trim whitespace
    cat >> "$JMX_FILE" << SAMPLEREOF
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Health: $endpoint">
          <stringProp name="HTTPSampler.domain">$(echo $BASE_URL | sed 's|https\?://||' | sed 's|/.*||')</stringProp>
          <stringProp name="HTTPSampler.protocol">$(echo $BASE_URL | grep -o '^https\?')</stringProp>
          <stringProp name="HTTPSampler.path">$endpoint</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
SAMPLEREOF
  done

  cat >> "$JMX_FILE" << 'JMXEOF'
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
JMXEOF

  # Replace placeholders
  sed -i "s/THREADS_PLACEHOLDER/$THREADS/g" "$JMX_FILE"
  sed -i "s/DURATION_PLACEHOLDER/$DURATION/g" "$JMX_FILE"
fi

echo "Running JMeter with plan: $JMX_FILE"

# Execute JMeter
jmeter -n \
  -t "$JMX_FILE" \
  -l "$OUTPUT_DIR/results.jtl" \
  -j "$OUTPUT_DIR/jmeter.log" \
  -e -o "$OUTPUT_DIR/html-report" \
  -JBASE_URL="$BASE_URL" \
  -JTHREADS="$THREADS" \
  -JDURATION="$DURATION"

EXIT_CODE=$?

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
  echo "RESULT: PASSED - Health checks completed"
else
  echo "RESULT: FAILED - Health checks had errors (exit: $EXIT_CODE)"
fi
echo "============================================================"

exit $EXIT_CODE
