#!/usr/bin/env bash
set -euo pipefail

# Launch EC2 workers to run distributed evolutionary searches.
#
# Outputs are uploaded to:
# s3://<bucket>/<out-prefix>/<run-id>/worker_<i>_summary.json
# s3://<bucket>/<out-prefix>/<run-id>/worker_<i>_runs.jsonl
#
# Mapping file written to:
# research_logs/aws_evolution_worker_map_<run-id>.jsonl

REGION="us-east-1"
COUNT=0
INSTANCE_TYPE="c7i.large"
KEY_NAME="codex-soldem-ed25519"
SUBNET_ID=""
SG_ID=""
INSTANCE_PROFILE_NAME="soldem-dist-worker-profile"
BUCKET=""
ARTIFACT_KEY=""
OUT_PREFIX="evolution_runs"
SEED_BASE=20260330
NAME_PREFIX="soldem-evo-worker"
JOBS_PATH="research_logs/experiment_inputs/evolution_jobs_20260301.txt"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --count) COUNT="$2"; shift 2;;
    --instance-type) INSTANCE_TYPE="$2"; shift 2;;
    --key-name) KEY_NAME="$2"; shift 2;;
    --subnet-id) SUBNET_ID="$2"; shift 2;;
    --sg-id) SG_ID="$2"; shift 2;;
    --instance-profile-name) INSTANCE_PROFILE_NAME="$2"; shift 2;;
    --bucket) BUCKET="$2"; shift 2;;
    --artifact-key) ARTIFACT_KEY="$2"; shift 2;;
    --out-prefix) OUT_PREFIX="$2"; shift 2;;
    --seed-base) SEED_BASE="$2"; shift 2;;
    --name-prefix) NAME_PREFIX="$2"; shift 2;;
    --jobs-path) JOBS_PATH="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$BUCKET" || -z "$ARTIFACT_KEY" ]]; then
  echo "Missing required args: --bucket and --artifact-key"
  exit 1
fi

if [[ ! -f "$JOBS_PATH" ]]; then
  echo "Jobs file not found: $JOBS_PATH"
  exit 1
fi

mapfile -t JOBS < <(grep -v '^\s*#' "$JOBS_PATH" | sed '/^\s*$/d')
if [[ "${#JOBS[@]}" -eq 0 ]]; then
  echo "No jobs found in $JOBS_PATH"
  exit 1
fi

if [[ "$COUNT" -le 0 ]]; then
  COUNT="${#JOBS[@]}"
fi

if [[ -z "$SUBNET_ID" ]]; then
  SUBNET_ID=$(aws ec2 describe-subnets \
    --region "$REGION" \
    --filters Name=default-for-az,Values=true \
    --query 'Subnets[0].SubnetId' \
    --output text)
fi

if [[ -z "$SG_ID" ]]; then
  SG_ID=$(aws ec2 describe-security-groups \
    --region "$REGION" \
    --filters Name=group-name,Values=default \
    --query 'SecurityGroups[0].GroupId' \
    --output text)
fi

AMI_ID=$(aws ssm get-parameter \
  --region "$REGION" \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' \
  --output text)

RUN_ID="$(date +%Y%m%d-%H%M%S)"
LOCAL_MAP="research_logs/aws_evolution_worker_map_${RUN_ID}.jsonl"
mkdir -p research_logs
: > "$LOCAL_MAP"

echo "run_id=$RUN_ID"
echo "artifact=s3://$BUCKET/$ARTIFACT_KEY"
echo "mapping_file=$LOCAL_MAP"
echo "jobs=${#JOBS[@]}"
echo "count=$COUNT"

for i in $(seq 0 $((COUNT - 1))); do
  job_idx=$((i % ${#JOBS[@]}))
  JOB_ARGS="${JOBS[$job_idx]}"
  JOB_ARGS_B64=$(printf '%s' "$JOB_ARGS" | base64 | tr -d '\n')
  WORKER_SEED=$((SEED_BASE + (i * 100000)))

  SUMMARY_KEY="$OUT_PREFIX/$RUN_ID/worker_${i}_summary.json"
  JSONL_KEY="$OUT_PREFIX/$RUN_ID/worker_${i}_runs.jsonl"
  STDOUT_KEY="$OUT_PREFIX/$RUN_ID/worker_${i}_stdout.txt"
  NAME="${NAME_PREFIX}-${RUN_ID}-${i}"

  read -r -d '' USER_DATA <<EOF || true
#!/bin/bash
set -euxo pipefail
yum install -y tar gzip python3 git awscli
curl -LsSf https://astral.sh/uv/install.sh | sh
source /root/.local/bin/env
mkdir -p /opt/soldem
cd /opt/soldem
aws s3 cp "s3://$BUCKET/$ARTIFACT_KEY" code.tar.gz
tar -xzf code.tar.gz
uv sync
JOB_ARGS=\$(echo "$JOB_ARGS_B64" | base64 -d)
set +e
uv run python scripts/evolve_population.py \$JOB_ARGS --seed $WORKER_SEED --out-dir /opt/soldem/out > /opt/soldem/worker_stdout.txt 2>&1
RC=\$?
set -e
if [[ \$RC -ne 0 ]]; then
  echo "worker failed rc=\$RC" >> /opt/soldem/worker_stdout.txt
  aws s3 cp /opt/soldem/worker_stdout.txt "s3://$BUCKET/$STDOUT_KEY" || true
  shutdown -h now || true
  exit 0
fi
uv run python - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("/opt/soldem/out/evolution_summary.json").read_text(encoding="utf-8"))
summary["worker_idx"] = $i
summary["seed"] = $WORKER_SEED
summary["job_args"] = """$JOB_ARGS"""
Path("/opt/soldem/worker_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
PY
aws s3 cp /opt/soldem/worker_summary.json "s3://$BUCKET/$SUMMARY_KEY"
aws s3 cp /opt/soldem/out/evolution_runs.jsonl "s3://$BUCKET/$JSONL_KEY"
aws s3 cp /opt/soldem/worker_stdout.txt "s3://$BUCKET/$STDOUT_KEY"
shutdown -h now || true
EOF

  INSTANCE_ID=$(aws ec2 run-instances \
    --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --subnet-id "$SUBNET_ID" \
    --associate-public-ip-address \
    --iam-instance-profile "Name=$INSTANCE_PROFILE_NAME" \
    --user-data "$USER_DATA" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=soldem-evolution},{Key=RunId,Value=$RUN_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

  printf '{"run_id":"%s","worker_idx":%d,"instance_id":"%s","summary_key":"%s","jsonl_key":"%s","stdout_key":"%s","job_idx":%d,"job_args":"%s"}\n' \
    "$RUN_ID" "$i" "$INSTANCE_ID" "$SUMMARY_KEY" "$JSONL_KEY" "$STDOUT_KEY" "$job_idx" "$JOB_ARGS" >> "$LOCAL_MAP"
  echo "launched worker_idx=$i instance_id=$INSTANCE_ID job_idx=$job_idx"
done

echo "done run_id=$RUN_ID"
echo "worker mapping in $LOCAL_MAP"
