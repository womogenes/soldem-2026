#!/usr/bin/env bash
set -euo pipefail

API_URL="http://127.0.0.1:8000"
PB_URL=""
WITH_TESTS=0
WITH_WEB=0
WITH_BEDROCK=0
WITH_POLICY_SMOKE=0
WITH_ADVISOR_SMOKE=0
BEDROCK_REGION="us-east-1"

usage() {
  cat <<'EOF'
Usage: scripts/day_of_preflight.sh [options]

Options:
  --api-url URL         Advisor API base URL (default: http://127.0.0.1:8000)
  --pb-url URL          PocketBase base URL (optional)
  --with-tests          Run backend unit tests
  --with-web            Run frontend check
  --with-bedrock        Run Bedrock smoke test
  --with-policy-smoke   Run first-place policy routing smoke check against API
  --with-advisor-smoke  Run advisor payload-normalization smoke check against API
  --bedrock-region R    Bedrock region (default: us-east-1)
  -h, --help            Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-url)
      API_URL="$2"
      shift 2
      ;;
    --pb-url)
      PB_URL="$2"
      shift 2
      ;;
    --with-tests)
      WITH_TESTS=1
      shift
      ;;
    --with-web)
      WITH_WEB=1
      shift
      ;;
    --with-bedrock)
      WITH_BEDROCK=1
      shift
      ;;
    --with-policy-smoke)
      WITH_POLICY_SMOKE=1
      shift
      ;;
    --with-advisor-smoke)
      WITH_ADVISOR_SMOKE=1
      shift
      ;;
    --bedrock-region)
      BEDROCK_REGION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

echo "== preflight start =="
date '+%Y-%m-%d %H:%M:%S %Z'
echo "api_url=$API_URL"

echo "-- api health"
curl -fsS "$API_URL/health" >/dev/null
echo "ok"

echo "-- api session state"
curl -fsS "$API_URL/session/state" >/dev/null
echo "ok"

if [[ -n "$PB_URL" ]]; then
  echo "-- pocketbase health"
  curl -fsS "$PB_URL/api/health" >/dev/null
  echo "ok"
fi

if [[ "$WITH_TESTS" -eq 1 ]]; then
  echo "-- backend tests"
  uv run -m unittest discover -s tests -v
fi

if [[ "$WITH_WEB" -eq 1 ]]; then
  echo "-- web check"
  pnpm -C web check
fi

if [[ "$WITH_BEDROCK" -eq 1 ]]; then
  echo "-- bedrock smoke ($BEDROCK_REGION)"
  bash scripts/aws/bedrock_smoke_test.sh "$BEDROCK_REGION"
fi

if [[ "$WITH_POLICY_SMOKE" -eq 1 ]]; then
  echo "-- policy smoke"
  uv run python scripts/policy_smoke.py --api "$API_URL"
fi

if [[ "$WITH_ADVISOR_SMOKE" -eq 1 ]]; then
  echo "-- advisor smoke"
  uv run python scripts/advisor_smoke.py --api "$API_URL"
fi

echo "== preflight complete =="
