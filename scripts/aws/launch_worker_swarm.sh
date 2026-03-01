#!/usr/bin/env bash
set -euo pipefail

# Launch N EC2 workers that can run simulation jobs and heartbeat into PocketBase.
# Usage:
# scripts/aws/launch_worker_swarm.sh --key-name my-key --count 4 --repo git@github.com:org/repo.git --pocketbase-url http://x.x.x.x:8090 --job-cmd "uv run python scripts/run_population.py ..."

REGION="us-east-1"
COUNT=2
INSTANCE_TYPE="c7i.large"
NAME_PREFIX="soldem-worker"
KEY_NAME=""
REPO_URL=""
BRANCH="main"
POCKETBASE_URL=""
WORKER_ROLE="sim"
ADMIN_TOKEN=""
JOB_CMD=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --count) COUNT="$2"; shift 2;;
    --instance-type) INSTANCE_TYPE="$2"; shift 2;;
    --name-prefix) NAME_PREFIX="$2"; shift 2;;
    --key-name) KEY_NAME="$2"; shift 2;;
    --repo) REPO_URL="$2"; shift 2;;
    --branch) BRANCH="$2"; shift 2;;
    --pocketbase-url) POCKETBASE_URL="$2"; shift 2;;
    --worker-role) WORKER_ROLE="$2"; shift 2;;
    --admin-token) ADMIN_TOKEN="$2"; shift 2;;
    --job-cmd) JOB_CMD="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$KEY_NAME" || -z "$REPO_URL" || -z "$POCKETBASE_URL" ]]; then
  echo "Missing required args. Need --key-name --repo --pocketbase-url"
  exit 1
fi

AMI_ID=$(aws ssm get-parameter \
  --region "$REGION" \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' --output text)

SUBNET_ID=$(aws ec2 describe-subnets --region "$REGION" --filters Name=default-for-az,Values=true --query 'Subnets[0].SubnetId' --output text)
SG_ID=$(aws ec2 describe-security-groups --region "$REGION" --filters Name=group-name,Values=default --query 'SecurityGroups[0].GroupId' --output text)

for i in $(seq 1 "$COUNT"); do
  NAME="${NAME_PREFIX}-${i}"
  WORKER_ID="${NAME}-$(date +%s)"

  read -r -d '' USER_DATA <<EOF || true
#!/bin/bash
set -euxo pipefail
cd /opt
yum install -y git unzip tar gzip python3
curl -LsSf https://astral.sh/uv/install.sh | sh
source /root/.local/bin/env
git clone --branch "$BRANCH" "$REPO_URL" soldem
cd soldem
python3 scripts/worker_heartbeat.py --base-url "$POCKETBASE_URL" --admin-token "$ADMIN_TOKEN" --worker-id "$WORKER_ID" --role "$WORKER_ROLE" --status "booted" || true
source /root/.local/bin/env
cd /opt/soldem
uv sync
python3 scripts/worker_heartbeat.py --base-url "$POCKETBASE_URL" --admin-token "$ADMIN_TOKEN" --worker-id "$WORKER_ID" --role "$WORKER_ROLE" --status "ready" || true
if [[ -n "$JOB_CMD" ]]; then
  if bash -lc "$JOB_CMD" >>/opt/soldem/worker_job.log 2>&1; then
    python3 scripts/worker_heartbeat.py --base-url "$POCKETBASE_URL" --admin-token "$ADMIN_TOKEN" --worker-id "$WORKER_ID" --role "$WORKER_ROLE" --status "completed" || true
  else
    python3 scripts/worker_heartbeat.py --base-url "$POCKETBASE_URL" --admin-token "$ADMIN_TOKEN" --worker-id "$WORKER_ID" --role "$WORKER_ROLE" --status "failed" || true
  fi
fi
EOF

  INSTANCE_ID=$(aws ec2 run-instances \
    --region "$REGION" \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --subnet-id "$SUBNET_ID" \
    --associate-public-ip-address \
    --user-data "$USER_DATA" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME}]" \
    --query 'Instances[0].InstanceId' --output text)

  echo "$NAME $INSTANCE_ID"
done
