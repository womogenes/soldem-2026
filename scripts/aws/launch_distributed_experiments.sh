#!/usr/bin/env bash
set -euo pipefail

# Launch an EC2 worker fleet that downloads a code artifact and runs
# distributed tournament scenarios, one shard per worker.
#
# Usage example:
# scripts/aws/launch_distributed_experiments.sh \
#   --bucket soldem-2026-... \
#   --artifact-key artifacts/soldem_v5_<sha>.tar.gz \
#   --count 8

REGION="us-east-1"
COUNT=8
INSTANCE_TYPE="c7i.large"
KEY_NAME="codex-soldem-ed25519"
SUBNET_ID=""
SG_ID=""
INSTANCE_PROFILE_NAME="soldem-dist-worker-profile"
BUCKET=""
ARTIFACT_KEY=""
OUT_PREFIX="distributed_runs"
N_MATCHES=35
SEED_BASE=20260301
NAME_PREFIX="soldem-dist-worker"
STRATEGIES_FILE=""
SCENARIO_PRESET="full"

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
    --n-matches) N_MATCHES="$2"; shift 2;;
    --seed-base) SEED_BASE="$2"; shift 2;;
    --name-prefix) NAME_PREFIX="$2"; shift 2;;
    --strategies-file) STRATEGIES_FILE="$2"; shift 2;;
    --scenario-preset) SCENARIO_PRESET="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$BUCKET" || -z "$ARTIFACT_KEY" ]]; then
  echo "Missing required args: --bucket and --artifact-key"
  exit 1
fi

DEFAULT_STRATEGIES_JSON='[
  "random",
  "pot_fraction",
  "delta_value",
  "conservative",
  "bully",
  "seller_profit",
  "adaptive_profile",
  "seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2",
  "seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2",
  "seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2",
  "seller_extraction:opportunistic_delta=2600,reserve_bid_floor=0.023,sell_count=2",
  "seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2",
  "seller_extraction:opportunistic_delta=4200,reserve_bid_floor=0.054,sell_count=2",
  "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2",
  "seller_extraction:opportunistic_delta=3600,reserve_bid_floor=0.06,sell_count=2",
  "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2",
  "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2",
  "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1",
  "risk_sniper:bid_scale=0.769,late_round_bonus=0.311,sell_count=2,stack_cap_fraction=0.258,trigger_delta=1600"
]'

if [[ -n "$STRATEGIES_FILE" ]]; then
  if [[ ! -f "$STRATEGIES_FILE" ]]; then
    echo "Strategies file not found: $STRATEGIES_FILE"
    exit 1
  fi
  STRATEGIES_JSON=$(python3 - <<'PY' "$STRATEGIES_FILE"
import json
from pathlib import Path
import sys

path = Path(sys.argv[1])
rows = []
for line in path.read_text(encoding="utf-8").splitlines():
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    rows.append(s)
print(json.dumps(rows))
PY
)
else
  STRATEGIES_JSON="$DEFAULT_STRATEGIES_JSON"
fi

STRATEGIES_B64=$(printf '%s' "$STRATEGIES_JSON" | base64 | tr -d '\n')

OBJECTIVES_JSON='["ev","first_place","robustness"]'
case "$SCENARIO_PRESET" in
  fast)
    PROFILES_JSON='["baseline_v1","standard_rankings"]'
    HORIZONS_JSON='[10]'
    CORR_SPECS_JSON='[
      ["none","none",0.0,[]],
      ["respect","respect",0.35,[[1,2]]],
      ["kingmaker","kingmaker",0.35,[[0,1]]]
    ]'
    ;;
  medium)
    PROFILES_JSON='["baseline_v1","standard_rankings","seller_self_bid"]'
    HORIZONS_JSON='[5,10]'
    CORR_SPECS_JSON='[
      ["none","none",0.0,[]],
      ["respect","respect",0.35,[[1,2]]],
      ["herd","herd",0.30,[[3,4]]]
    ]'
    ;;
  full)
    PROFILES_JSON='[
      "baseline_v1",
      "standard_rankings",
      "seller_self_bid",
      "top2_split",
      "high_low_split",
      "single_card_sell"
    ]'
    HORIZONS_JSON='[5,10,20]'
    CORR_SPECS_JSON='[
      ["none","none",0.0,[]],
      ["respect","respect",0.35,[[1,2]]],
      ["herd","herd",0.30,[[3,4]]],
      ["kingmaker","kingmaker",0.35,[[0,1]]]
    ]'
    ;;
  *)
    echo "Unknown scenario preset: $SCENARIO_PRESET (use fast|medium|full)"
    exit 1
    ;;
esac

PROFILES_B64=$(printf '%s' "$PROFILES_JSON" | base64 | tr -d '\n')
OBJECTIVES_B64=$(printf '%s' "$OBJECTIVES_JSON" | base64 | tr -d '\n')
HORIZONS_B64=$(printf '%s' "$HORIZONS_JSON" | base64 | tr -d '\n')
CORR_SPECS_B64=$(printf '%s' "$CORR_SPECS_JSON" | base64 | tr -d '\n')

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
LOCAL_MAP="research_logs/aws_worker_map_${RUN_ID}.jsonl"
mkdir -p research_logs
: > "$LOCAL_MAP"

echo "run_id=$RUN_ID"
echo "artifact=s3://$BUCKET/$ARTIFACT_KEY"
echo "mapping_file=$LOCAL_MAP"
echo "scenario_preset=$SCENARIO_PRESET"

for i in $(seq 0 $((COUNT - 1))); do
  RESULT_KEY="$OUT_PREFIX/$RUN_ID/worker_${i}.json"
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
uv run python - <<'PY'
import base64
import json
from sim import CorrelationModel, run_population_tournament

worker_idx = $i
worker_count = $COUNT
n_matches = $N_MATCHES
seed_base = $SEED_BASE

strategies = json.loads(base64.b64decode("$STRATEGIES_B64").decode("utf-8"))
profiles = json.loads(base64.b64decode("$PROFILES_B64").decode("utf-8"))
objectives = json.loads(base64.b64decode("$OBJECTIVES_B64").decode("utf-8"))
horizons = json.loads(base64.b64decode("$HORIZONS_B64").decode("utf-8"))
corr_specs = json.loads(base64.b64decode("$CORR_SPECS_B64").decode("utf-8"))
correlations = []
for name, mode, strength, pairs in corr_specs:
    correlations.append(
        (
            name,
            CorrelationModel(
                mode=mode,
                strength=float(strength),
                pairs=[tuple(x) for x in pairs],
            ),
        )
    )

scenarios = []
for p in profiles:
    for o in objectives:
        for h in horizons:
            for cname, cmodel in correlations:
                scenarios.append((p, o, h, cname, cmodel))

rows = []
for idx, (profile, objective, horizon, corr_name, corr_model) in enumerate(scenarios):
    if idx % worker_count != worker_idx:
        continue
    seed = seed_base + (worker_idx * 100000) + idx
    out = run_population_tournament(
        strategies,
        n_matches=n_matches,
        n_games_per_match=horizon,
        rule_profile=profile,
        seed=seed,
        objective=objective,
        correlation=corr_model,
    )
    key = "expected_pnl" if objective == "ev" else (
        "first_place_rate" if objective == "first_place" else "robustness"
    )
    winner = max(out["leaderboard"], key=lambda r: r[key])
    rows.append(
        {
            "worker_idx": worker_idx,
            "scenario_idx": idx,
            "profile": profile,
            "objective": objective,
            "horizon": horizon,
            "correlation": corr_name,
            "seed": seed,
            "metric_key": key,
            "winner_tag": winner["tag"],
            "winner_metric": winner[key],
            "leaderboard": out["leaderboard"],
        }
    )

payload = {
    "worker_idx": worker_idx,
    "worker_count": worker_count,
    "n_matches": n_matches,
    "rows": rows,
}
with open("/opt/soldem/worker_result.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
PY
aws s3 cp /opt/soldem/worker_result.json "s3://$BUCKET/$RESULT_KEY"
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
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=soldem-dist},{Key=RunId,Value=$RUN_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

  printf '{"run_id":"%s","worker_idx":%d,"instance_id":"%s","result_key":"%s","name":"%s"}\n' \
    "$RUN_ID" "$i" "$INSTANCE_ID" "$RESULT_KEY" "$NAME" >> "$LOCAL_MAP"
  echo "launched worker_idx=$i instance_id=$INSTANCE_ID"
done

echo "done run_id=$RUN_ID"
echo "worker mapping in $LOCAL_MAP"
