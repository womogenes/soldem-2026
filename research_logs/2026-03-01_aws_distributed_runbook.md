# AWS distributed runbook

Local timestamp: 2026-03-01 06:46:09 PST

## Purpose

Run large experiment grids in parallel on EC2, collect outputs from S3, and sync champion evidence to PocketBase.

## Components added

- Launcher: `scripts/aws/launch_distributed_experiments.sh`
- Collector: `scripts/aws/collect_distributed_results.py`
- Continuous loop orchestrator: `scripts/aws/continuous_distributed_loop.sh`
- Param sweep launcher: `scripts/aws/launch_param_sweep_experiments.sh`
- Param sweep collector: `scripts/aws/collect_param_sweep_results.py`
- Evolution launcher: `scripts/aws/launch_evolution_experiments.sh`
- Evolution collector: `scripts/aws/collect_evolution_results.py`
- Distributed summary synthesizer: `scripts/aws/summarize_distributed_champions.py`
- Strategy pool builder: `scripts/aws/build_strategy_pool.py`
- PocketBase schema bootstrap: `scripts/pocketbase/apply_collections.py`
- PocketBase artifact sync: `scripts/pocketbase/sync_discovery.py`

## AWS resources used

- S3 bucket:
  - `soldem-2026-539881456097-1772358537`
- IAM role:
  - `soldem-dist-worker-role`
- IAM instance profile:
  - `soldem-dist-worker-profile`
- PocketBase instances:
  - earlier node: `http://3.238.237.186:8090`
  - active synced node (key-accessible): `http://3.236.115.133:8090`

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
- Run `20260301-023132`
  - 12x `c7i.large`
  - scenarios: 216
  - `n_matches=180` per scenario shard configuration
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 206
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 9
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 1
- Run `20260301-030400` (expanded strategy pool with `reserve_bid_floor=0.06` variants)
  - 12x `c7i.large`
  - scenarios: 216
  - `n_matches=180` per scenario shard configuration
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`: 105
    - `seller_extraction:opportunistic_delta=3600,reserve_bid_floor=0.06,sell_count=2`: 105
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 4
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 2
- Run `20260301-031824` (larger expanded pool including evolution-discovered candidates)
  - 12x `c7i.large`
  - scenarios: 216
  - `n_matches=240` per scenario shard configuration
  - winner counts:
    - `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`: 90
    - `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`: 43
    - `pot_fraction`: 15
    - `bully`: 15
    - `seller_profit`: 7
    - `adaptive_profile`: 6

Combined distributed total across four high-confidence runs:

- scenarios: 864
- champion wins: 777 (`seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`)

Note: run `20260301-030400` used an expanded strategy pool and should be treated as upgrade validation, not merged into the older 864-scenario pool summary.

## Additional EC2 search runs completed

- Param sweep run `20260301-024646`:
  - outputs: `research_logs/experiment_outputs/param_sweep_20260301-024646/aggregate_summary.json`
  - strongest candidate vs old champion:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`
    - mean delta `+19.424` over 108 scenarios.
- Targeted param sweep run `20260301-033100`:
  - outputs: `research_logs/experiment_outputs/param_sweep_20260301-033100/aggregate_summary.json`
  - champion fixed to:
    - `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
  - challenger result:
    - best challenger `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
    - mean delta vs champion `-1.475` (46 wins, 62 losses)
  - conclusion: retain `3300/0.029/2` as session champion.
- Evolution runs:
  - `20260301-025553`:
    - outputs: `research_logs/experiment_outputs/evolution_20260301-025553/aggregate_summary.json`
    - candidate pool: `research_logs/experiment_inputs/evolution_candidate_pool_20260301-025553.txt`
  - `20260301-025732`:
    - outputs: `research_logs/experiment_outputs/evolution_20260301-025732/aggregate_summary.json`
    - candidate pool: `research_logs/experiment_inputs/evolution_candidate_pool_20260301-025732.txt`
  - `20260301-044713`:
    - outputs: `research_logs/experiment_outputs/evolution_20260301-044713/aggregate_summary.json`
    - candidate pool: `research_logs/experiment_inputs/evolution_candidate_pool_20260301-044713.txt`
- Distributed candidate validation run:
  - `20260301-045734`
  - outputs:
    - `research_logs/experiment_outputs/distributed_20260301-045734/aggregate_summary.json`
    - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-045734.json`
    - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-045734.json`
  - note: this run is stored as candidate-only and intentionally not auto-promoted to HUD defaults.
- Targeted param sweep promotion run:
  - failed attempt `20260301-050045` (artifact missing candidate specs file), instances terminated
  - corrected run `20260301-050721`:
    - outputs: `research_logs/experiment_outputs/param_sweep_20260301-050721/aggregate_summary.json`
    - horizon-10 extraction: `research_logs/experiment_outputs/horizon10_confirmation_20260301-050721.json`
    - promoted upgrade artifact:
      - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-050721.json`
    - promoted strategy:
      - `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- Human-focused high-match distributed run:
  - `20260301-061228`
  - 18x `c7i.large`
  - `n_matches=360`
  - pool excludes `random` and `pot_fraction`
  - outputs:
    - `research_logs/experiment_outputs/distributed_20260301-061228/aggregate_summary.json`
    - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-061228.json`
    - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-061228.json`
  - objective winner counts:
    - `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
    - `first_place`: `bully` (with objective-strength rank/margin favoring `seller_profit`)
    - `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- Merged promotion artifact across latest human-focused runs:
  - source runs:
    - `distributed_20260301-053816`
    - `distributed_20260301-061228`
  - merged aggregate:
    - `research_logs/experiment_outputs/distributed_20260301-062400-merged/aggregate_summary.json`
  - promoted upgrade:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-062400-merged.json`
  - promoted objective split:
    - `ev`: `5400/0.032/2`
    - `first_place`: `seller_profit`
    - `robustness`: `4400/0.02/2`
- Quick pre-7am exploitability check and conservative promotion:
  - launched param sweep `20260301-062640` (`n_matches=140`) but terminated early as too slow for deadline
  - completed quick param sweep `20260301-063621` (`n_matches=50`) against champion `5400/0.032/2`
  - output:
    - `research_logs/experiment_outputs/param_sweep_20260301-063621/aggregate_summary.json`
  - key result:
    - multiple challengers show positive mean delta vs `5400`, including `4500/0.02/2` and `4400/0.02/2`
  - conservative promoted artifact:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`
  - conservative objective split:
    - `ev`: `4400/0.02/2`
    - `first_place`: `seller_profit`
    - `robustness`: `4400/0.02/2`

Loop automation smoke runs:

- `20260301-022349` (manual recovery of early loop failure run)
- `20260301-022736` (full loop end-to-end validation run)

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

5. Build distributed champion summary artifacts:

```bash
uv run python scripts/aws/summarize_distributed_champions.py \
  --aggregate research_logs/experiment_outputs/distributed_<run_id>/aggregate_summary.json
```

6. Promote to active HUD defaults only after confirmation:

```bash
uv run python scripts/aws/summarize_distributed_champions.py \
  --aggregate research_logs/experiment_outputs/distributed_<run_id>/aggregate_summary.json \
  --promote-upgrade
```

7. Terminate completed workers:

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
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-023132.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-031824.json`
- `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-033100.json`
- `research_logs/experiment_outputs/distributed_20260301-061228/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-061228.json`
- `research_logs/experiment_outputs/distributed_20260301-062400-merged/aggregate_summary.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-062400-merged.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-062400-merged.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`
- `research_logs/experiment_outputs/param_sweep_20260301-063621/aggregate_summary.json`
- `research_logs/experiment_outputs/param_sweep_20260301-024646/aggregate_summary.json`
- `research_logs/experiment_outputs/param_sweep_20260301-033100/aggregate_summary.json`
- `research_logs/experiment_outputs/evolution_20260301-025553/aggregate_summary.json`
- `research_logs/experiment_outputs/evolution_20260301-025732/aggregate_summary.json`
