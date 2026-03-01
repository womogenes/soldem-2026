#!/usr/bin/env bash
set -euo pipefail

# Launch EC2 workers that run a parameter sweep against the current champion.
#
# Outputs are uploaded to:
# s3://<bucket>/<out-prefix>/<run-id>/worker_<i>.json

REGION="us-east-1"
COUNT=12
INSTANCE_TYPE="c7i.large"
KEY_NAME="codex-soldem-ed25519"
SUBNET_ID=""
SG_ID=""
INSTANCE_PROFILE_NAME="soldem-dist-worker-profile"
BUCKET=""
ARTIFACT_KEY=""
OUT_PREFIX="param_sweep_runs"
N_MATCHES=100
SEED_BASE=20260320
NAME_PREFIX="soldem-param-worker"
CANDIDATE_SPECS_PATH="research_logs/experiment_inputs/param_sweep_specs_20260301.txt"
CHAMPION_SPEC="seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2"

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
    --candidate-specs-path) CANDIDATE_SPECS_PATH="$2"; shift 2;;
    --champion-spec) CHAMPION_SPEC="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$BUCKET" || -z "$ARTIFACT_KEY" ]]; then
  echo "Missing required args: --bucket and --artifact-key"
  exit 1
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
LOCAL_MAP="research_logs/aws_param_sweep_worker_map_${RUN_ID}.jsonl"
mkdir -p research_logs
: > "$LOCAL_MAP"

echo "run_id=$RUN_ID"
echo "artifact=s3://$BUCKET/$ARTIFACT_KEY"
echo "mapping_file=$LOCAL_MAP"

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
import json
from pathlib import Path
from sim import CorrelationModel, run_population_tournament

worker_idx = $i
worker_count = $COUNT
n_matches = $N_MATCHES
seed_base = $SEED_BASE
champion = "$CHAMPION_SPEC"
candidate_path = Path("$CANDIDATE_SPECS_PATH")

base_pool = [
    "random",
    "pot_fraction",
    "delta_value",
    "conservative",
    "bully",
    "seller_profit",
    "adaptive_profile",
    champion,
    "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1",
    "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2",
    "risk_sniper:bid_scale=0.769,late_round_bonus=0.311,sell_count=2,stack_cap_fraction=0.258,trigger_delta=1600",
]

candidates = []
for line in candidate_path.read_text(encoding="utf-8").splitlines():
    spec = line.strip()
    if not spec or spec.startswith("#"):
        continue
    candidates.append(spec)

profiles = ["baseline_v1", "single_card_sell", "seller_self_bid"]
objectives = ["ev", "first_place", "robustness"]
horizons = [8, 10, 12]
correlations = [
    ("none", CorrelationModel(mode="none", strength=0.0, pairs=[])),
    ("respect", CorrelationModel(mode="respect", strength=0.35, pairs=[(1, 2)])),
    ("herd", CorrelationModel(mode="herd", strength=0.30, pairs=[(3, 4)])),
    ("kingmaker", CorrelationModel(mode="kingmaker", strength=0.35, pairs=[(0, 1)])),
]

rows = []
for cand_idx, candidate in enumerate(candidates):
    if cand_idx % worker_count != worker_idx:
        continue

    strategies = list(dict.fromkeys(base_pool + [candidate]))
    cand_rows = []
    for profile in profiles:
        for objective in objectives:
            metric_key = "expected_pnl" if objective == "ev" else (
                "first_place_rate" if objective == "first_place" else "robustness"
            )
            for horizon in horizons:
                for corr_name, corr in correlations:
                    seed = seed_base + (worker_idx * 1_000_000) + (cand_idx * 10_000) + (
                        profiles.index(profile) * 1000
                    ) + (objectives.index(objective) * 100) + (horizons.index(horizon) * 10) + (
                        ["none", "respect", "herd", "kingmaker"].index(corr_name)
                    )
                    out = run_population_tournament(
                        strategies,
                        n_matches=n_matches,
                        n_games_per_match=horizon,
                        rule_profile=profile,
                        seed=seed,
                        objective=objective,
                        correlation=corr,
                    )
                    board = out["leaderboard"]
                    cand_row = next(r for r in board if r["tag"] == candidate)
                    champ_row = next(r for r in board if r["tag"] == champion)
                    leader = max(board, key=lambda r: r[metric_key])["tag"]
                    cand_rows.append(
                        {
                            "candidate": candidate,
                            "profile": profile,
                            "objective": objective,
                            "horizon": horizon,
                            "correlation": corr_name,
                            "seed": seed,
                            "metric_key": metric_key,
                            "candidate_metric": cand_row[metric_key],
                            "champion_metric": champ_row[metric_key],
                            "delta_vs_champion": cand_row[metric_key] - champ_row[metric_key],
                            "leader_tag": leader,
                        }
                    )

    mean_delta = sum(r["delta_vs_champion"] for r in cand_rows) / max(1, len(cand_rows))
    wins = sum(1 for r in cand_rows if r["delta_vs_champion"] > 0)
    ties = sum(1 for r in cand_rows if abs(r["delta_vs_champion"]) < 1e-12)
    rows.append(
        {
            "candidate": candidate,
            "n_scenarios": len(cand_rows),
            "win_count_vs_champion": wins,
            "tie_count_vs_champion": ties,
            "mean_delta_vs_champion": mean_delta,
            "scenario_rows": cand_rows,
        }
    )

payload = {
    "worker_idx": worker_idx,
    "worker_count": worker_count,
    "n_matches": n_matches,
    "champion": champion,
    "candidate_specs_path": str(candidate_path),
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
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME},{Key=Project,Value=soldem-param-sweep},{Key=RunId,Value=$RUN_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

  printf '{"run_id":"%s","worker_idx":%d,"instance_id":"%s","result_key":"%s","name":"%s"}\n' \
    "$RUN_ID" "$i" "$INSTANCE_ID" "$RESULT_KEY" "$NAME" >> "$LOCAL_MAP"
  echo "launched worker_idx=$i instance_id=$INSTANCE_ID"
done

echo "done run_id=$RUN_ID"
echo "worker mapping in $LOCAL_MAP"
