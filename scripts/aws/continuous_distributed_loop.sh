#!/usr/bin/env bash
set -euo pipefail

# Repeatedly run distributed EC2 experiment batches until a cycle limit
# or wall-clock deadline is reached.
#
# Example:
# scripts/aws/continuous_distributed_loop.sh \
#   --bucket soldem-2026-... \
#   --artifact-key artifacts/soldem_v5_<sha>.tar.gz \
#   --cycles 3 \
#   --count 12 \
#   --n-matches 180 \
#   --sync-pocketbase-url http://x.x.x.x:8090 \
#   --sync-pocketbase-email admin@example.com \
#   --sync-pocketbase-password '...'

REGION="us-east-1"
BUCKET=""
ARTIFACT_KEY=""
CYCLES=1
COUNT=12
N_MATCHES=120
INSTANCE_TYPE="c7i.large"
INSTANCE_PROFILE_NAME="soldem-dist-worker-profile"
SEED_BASE=20260310
SLEEP_BETWEEN=30
WAIT_TIMEOUT_SECS=7200
UNTIL_EPOCH=0

SYNC_PB_URL=""
SYNC_PB_EMAIL=""
SYNC_PB_PASSWORD=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --artifact-key) ARTIFACT_KEY="$2"; shift 2;;
    --cycles) CYCLES="$2"; shift 2;;
    --count) COUNT="$2"; shift 2;;
    --n-matches) N_MATCHES="$2"; shift 2;;
    --instance-type) INSTANCE_TYPE="$2"; shift 2;;
    --instance-profile-name) INSTANCE_PROFILE_NAME="$2"; shift 2;;
    --seed-base) SEED_BASE="$2"; shift 2;;
    --sleep-between) SLEEP_BETWEEN="$2"; shift 2;;
    --wait-timeout-secs) WAIT_TIMEOUT_SECS="$2"; shift 2;;
    --until-epoch) UNTIL_EPOCH="$2"; shift 2;;
    --sync-pocketbase-url) SYNC_PB_URL="$2"; shift 2;;
    --sync-pocketbase-email) SYNC_PB_EMAIL="$2"; shift 2;;
    --sync-pocketbase-password) SYNC_PB_PASSWORD="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$BUCKET" || -z "$ARTIFACT_KEY" ]]; then
  echo "Missing required args: --bucket and --artifact-key"
  exit 1
fi

mkdir -p research_logs
LOOP_LOG="research_logs/aws_continuous_loop_$(date +%Y%m%d-%H%M%S).log"
echo "loop_log=$LOOP_LOG"

for cycle in $(seq 1 "$CYCLES"); do
  now_epoch=$(date +%s)
  if [[ "$UNTIL_EPOCH" -gt 0 && "$now_epoch" -ge "$UNTIL_EPOCH" ]]; then
    echo "Reached UNTIL_EPOCH=$UNTIL_EPOCH; exiting loop" | tee -a "$LOOP_LOG"
    break
  fi

  run_seed=$((SEED_BASE + cycle))
  echo "=== cycle $cycle seed=$run_seed ===" | tee -a "$LOOP_LOG"

  launch_out=$(scripts/aws/launch_distributed_experiments.sh \
    --region "$REGION" \
    --bucket "$BUCKET" \
    --artifact-key "$ARTIFACT_KEY" \
    --count "$COUNT" \
    --instance-type "$INSTANCE_TYPE" \
    --n-matches "$N_MATCHES" \
    --seed-base "$run_seed" \
    --instance-profile-name "$INSTANCE_PROFILE_NAME")
  echo "$launch_out" | tee -a "$LOOP_LOG"

  map_file=$(echo "$launch_out" | awk -F= '/^mapping_file=/{print $2}')
  if [[ -z "$map_file" || ! -f "$map_file" ]]; then
    echo "Failed to locate mapping file from launch output" | tee -a "$LOOP_LOG"
    exit 1
  fi

  run_id=$(python - <<PY
import json
with open("$map_file","r",encoding="utf-8") as f:
    line=next((ln for ln in f if ln.strip()),"")
print(json.loads(line)["run_id"] if line else "")
PY
)
  if [[ -z "$run_id" ]]; then
    echo "Failed to parse run_id from $map_file" | tee -a "$LOOP_LOG"
    exit 1
  fi

  expected=$(wc -l < "$map_file")
  echo "run_id=$run_id expected_files=$expected" | tee -a "$LOOP_LOG"

  start_wait=$(date +%s)
  while true; do
    have=$(aws s3 ls "s3://$BUCKET/distributed_runs/$run_id/" 2>/dev/null | wc -l)
    echo "run_id=$run_id files=$have/$expected" | tee -a "$LOOP_LOG"
    if [[ "$have" -ge "$expected" ]]; then
      break
    fi
    now=$(date +%s)
    if [[ $((now - start_wait)) -ge "$WAIT_TIMEOUT_SECS" ]]; then
      echo "Timeout waiting for run_id=$run_id outputs" | tee -a "$LOOP_LOG"
      break
    fi
    sleep "$SLEEP_BETWEEN"
  done

  if [[ -n "$SYNC_PB_URL" && -n "$SYNC_PB_EMAIL" && -n "$SYNC_PB_PASSWORD" ]]; then
    pb_token=$(curl -sS -X POST "$SYNC_PB_URL/api/collections/_superusers/auth-with-password" \
      -H 'content-type: application/json' \
      -d "{\"identity\":\"$SYNC_PB_EMAIL\",\"password\":\"$SYNC_PB_PASSWORD\"}" \
      | python -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
  else
    pb_token=""
  fi

  collect_cmd=(
    uv run python scripts/aws/collect_distributed_results.py
    --bucket "$BUCKET"
    --mapping-file "$map_file"
  )
  if [[ -n "$pb_token" && -n "$SYNC_PB_URL" ]]; then
    collect_cmd+=(--sync-pocketbase-url "$SYNC_PB_URL" --sync-pocketbase-token "$pb_token")
  fi
  "${collect_cmd[@]}" | tee -a "$LOOP_LOG"

  ids=$(python - <<PY
import json
ids=[]
with open("$map_file","r",encoding="utf-8") as f:
    for ln in f:
        if ln.strip():
            ids.append(json.loads(ln)["instance_id"])
print(" ".join(ids))
PY
)
  if [[ -n "$ids" ]]; then
    aws ec2 terminate-instances --region "$REGION" --instance-ids $ids \
      --query 'TerminatingInstances[].InstanceId' --output text | tee -a "$LOOP_LOG"
  fi
done

echo "continuous loop complete" | tee -a "$LOOP_LOG"
