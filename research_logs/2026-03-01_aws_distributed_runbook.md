# AWS distributed runbook

Local timestamp: 2026-03-01 02:08:17 PST

## Purpose

Run large experiment grids in parallel on EC2, collect outputs from S3, and sync champion evidence to PocketBase.

## Components added

- Launcher: `scripts/aws/launch_distributed_experiments.sh`
- Collector: `scripts/aws/collect_distributed_results.py`
- Continuous loop orchestrator: `scripts/aws/continuous_distributed_loop.sh`
- PocketBase schema bootstrap: `scripts/pocketbase/apply_collections.py`
- PocketBase artifact sync: `scripts/pocketbase/sync_discovery.py`

## AWS resources used

- S3 bucket:
  - `soldem-2026-539881456097-1772358537`
- IAM role:
  - `soldem-dist-worker-role`
- IAM instance profile:
  - `soldem-dist-worker-profile`
- Fresh PocketBase instance:
  - `http://3.238.237.186:8090`

## Distributed runs completed

- Run `20260301-015615`
  - 8x `c7i.large`
  - scenarios: 216
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 160
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 44
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 11
    - `conservative`: 1
- Run `20260301-020134`
  - 12x `c7i.large`
  - scenarios: 216
  - `n_matches=120` per scenario shard configuration
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 199
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 11
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 6
- Run `20260301-021037`
  - 12x `c7i.large`
  - scenarios: 216
  - `n_matches=250` per scenario shard configuration
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 212
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 4

Combined distributed total across three runs:

- scenarios: 648
- champion wins: 571 (`seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`)

## Standard run flow

1. Build and upload artifact tarball:

```bash
git archive --format=tar.gz --output=/tmp/soldem.tar.gz HEAD
aws s3 cp /tmp/soldem.tar.gz s3://<bucket>/artifacts/soldem.tar.gz
```

2. Launch distributed workers:

```bash
scripts/aws/launch_distributed_experiments.sh \
  --bucket <bucket> \
  --artifact-key artifacts/soldem.tar.gz \
  --count 12 \
  --instance-type c7i.large \
  --n-matches 120 \
  --instance-profile-name soldem-dist-worker-profile
```

3. Collect outputs:

```bash
uv run python scripts/aws/collect_distributed_results.py \
  --bucket <bucket> \
  --mapping-file research_logs/aws_worker_map_<run_id>.jsonl
```

4. Sync into PocketBase:

```bash
uv run python scripts/aws/collect_distributed_results.py \
  --bucket <bucket> \
  --mapping-file research_logs/aws_worker_map_<run_id>.jsonl \
  --sync-pocketbase-url http://<pb-host>:8090 \
  --sync-pocketbase-token <pb-superuser-token>
```

5. Terminate completed workers:

```bash
aws ec2 terminate-instances --instance-ids <ids...> --region us-east-1
```

## Continuous overnight mode

Use when you want repeated improvement cycles until a deadline:

```bash
scripts/aws/continuous_distributed_loop.sh \
  --bucket <bucket> \
  --artifact-key artifacts/soldem.tar.gz \
  --cycles 6 \
  --count 12 \
  --n-matches 180 \
  --sync-pocketbase-url http://<pb-host>:8090 \
  --sync-pocketbase-email <admin-email> \
  --sync-pocketbase-password <admin-password>
```

## Result artifacts

- `research_logs/experiment_outputs/distributed_20260301-015615/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_20260301-020134/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-015615.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-020134.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-021037.json`
- `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
