# Execution log

Local timezone: PST (America/Los_Angeles)

## 2026-03-01 01:29:41 PST

- Loaded `RULES.md`, `game/engine_base.py`, `game/utils.py`, simulation scripts, AWS scripts, and web HUD implementation.
- Confirmed existing baseline includes strategy plugin loading, population tournaments, correlation models, FastAPI advisor, and Svelte HUD.
- Confirmed `research_logs/000_god_prompt.md` exists and mirrors the goal/spec for compaction continuity.

## 2026-03-01 01:38:16 PST

- Recomputed exact 50-card five-card category frequencies by exhaustive enumeration over `C(50,5)=2,118,760` hands.
- Verified counts in `game/utils.py` are correct:
  - five_kind=10, straight_flush=30, flush=1230, four_kind=2250, full_house=9000, straight=18720, three_kind=90000, two_pair=180000, high_card=767520, one_pair=1050000.
- Added advanced strategy family in `strategies/advanced.py`:
  - `prob_value`, `risk_sniper`, `seller_extraction`.
- Added parameterized built-in strategy loading (spec format `tag:param=value,...`) via `strategies/loader.py`.
- Added evolutionary search runner `scripts/evolve_population.py`.
- Added tests:
  - `tests/test_strategy_loader.py`
  - `tests/test_advisor.py`
- Test suite status: `10/10` passing (`uv run python -m unittest discover -s tests -v`).
- Experiment outputs generated:
  - `research_logs/experiment_outputs/baseline_population_seed42.json`
  - `research_logs/experiment_outputs/evolution_runs.jsonl`
  - `research_logs/experiment_outputs/evolution_summary.json`
  - `research_logs/experiment_outputs/champion_validation_matrix.json`
  - `research_logs/experiment_outputs/rule_profile_validation.json`
  - `research_logs/experiment_outputs/large_validation_baseline_respect.json`
- Current best strategy spec across tested scenarios:
  - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`.

## 2026-03-01 01:40:32 PST

- Completed literature review and practical translation to Sold 'Em in:
  - `research_logs/2026-03-01_literature_review.md`.
- Coverage includes:
  - first-price auction theory
  - winner's curse and human bidding behavior
  - CFR/MCCFR/Deep CFR/NFSP/Libratus/Pluribus
  - safe exploitation and opponent modeling
  - PSRO/population training and non-transitivity handling
- Included actionable recommendations for:
  - bidding and selling policy design
  - profile-driven adaptation against humans
  - robust population search with collusion/correlation stress tests.

## 2026-03-01 01:44:14 PST

- Patched advisor/API integration for parameterized strategy tags:
  - `game/advisor.py` now uses `strategies.loader.load_strategy(...)`.
  - `game/api.py` default champions set to tuned `seller_extraction` spec.
  - `game/api.py` recompute champion pool extended with tuned candidate specs.
- Added PocketBase sync tooling:
  - `sim/pocketbase_client.py` gained authenticated superuser login and request helper.
  - `scripts/pocketbase/sync_discovery.py` uploads discovered strategies/champions/eval runs.
- Updated AWS worker orchestration:
  - `scripts/aws/launch_worker_swarm.sh` now supports `--job-cmd` and authenticated heartbeat statuses (`booted`, `ready`, `completed`, `failed`).
- AWS CLI usage and readiness checks:
  - `aws sts get-caller-identity` succeeded (account reachable).
  - `scripts/aws/bedrock_smoke_test.sh us-east-1` succeeded (Bedrock model list returned).
  - Verified existing running PocketBase instance responds at `http://44.221.42.217:8090/api/health`.
- Day-of operations doc added:
  - `research_logs/2026-03-01_day_of_patch_guide.md` (2-minute patch workflow + weird-rule checklist).
- Full-stack validation:
  - Backend `uvicorn game.api:app` health endpoint OK.
  - Session state confirms champion default strategy is tuned `seller_extraction` spec.
  - Web checks/build succeeded (`pnpm run check`, `pnpm run build`).

## 2026-03-01 01:45:09 PST

- Added consolidated operator summary:
  - `research_logs/2026-03-01_system_summary.md`.
- Included direct run commands for backend, HUD, recompute, evolution, and PocketBase sync.
- Added explicit note for future compaction to keep `research_logs/000_god_prompt.md` as spec anchor.

## 2026-03-01 01:45:09 PST

- Added strategy format doc:
  - `strategies/strategy_format.md`.
- Added human-operator playbook:
  - `research_logs/2026-03-01_human_playbook.md`.
- Purpose:
  - train human execution on top of discovered champion
  - provide concise decision rules for live 10-game format.

## 2026-03-01 01:46:21 PST

- Generated precomputed variation champion map:
  - `research_logs/experiment_outputs/precomputed_variation_champions.json`.
- Updated consolidated summary to include:
  - human playbook
  - strategy format doc
  - precomputed variation mapping artifact.

## 2026-03-01 01:57:37 PST

- AWS/EC2 distributed experimentation pipeline work:
  - Created S3 bucket for run artifacts/results: `soldem-2026-539881456097-1772358537`.
  - Uploaded code artifact tarball from commit `e5f3ced`:
    - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v5_e5f3ced.tar.gz`
  - Added scripts:
    - `scripts/aws/launch_distributed_experiments.sh`
    - `scripts/aws/collect_distributed_results.py`
- Created and configured IAM resources for workers:
  - role: `soldem-dist-worker-role`
  - instance profile: `soldem-dist-worker-profile`
  - inline S3 policy scoped to bucket above.
- Launched and debugged EC2 worker fleets:
  - Initial run `20260301-015114` failed due unsupported `aws s3 presign --http-method PUT`.
  - Second run `20260301-015448` failed due `curl` package conflict and system-python execution.
  - Patched launcher:
    - switched to instance-profile S3 upload
    - removed `curl` install conflict
    - switched worker execution to `uv run python`.
  - Relaunched corrected run:
    - run id: `20260301-015615`
    - 8x `c7i.large`
    - mapping file: `research_logs/aws_worker_map_20260301-015615.jsonl`
- Provisioned fresh PocketBase EC2 node:
  - instance id: `i-0a229522e15035179`
  - URL: `http://3.238.237.186:8090`
  - created superuser via SSH CLI bootstrap (`pocketbase superuser upsert`).
- Added PocketBase collection bootstrap script:
  - `scripts/pocketbase/apply_collections.py`
  - applied schema successfully to fresh node (`strategies`, `eval_runs`, `match_results`, `champions`, `workers`).

## 2026-03-01 02:08:17 PST

- Completed corrected distributed run `20260301-015615`:
  - 8x `c7i.large`, 216 scenarios, all shards uploaded.
  - Aggregate winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 160
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 44
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 11
    - `conservative`: 1
- Completed larger distributed run `20260301-020134`:
  - 12x `c7i.large`, `n_matches=120`, 216 scenarios, all shards uploaded.
  - Aggregate winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 199
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 11
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 6
- Collected and stored distributed artifacts:
  - `research_logs/experiment_outputs/distributed_20260301-015615/aggregate_summary.json`
  - `research_logs/experiment_outputs/distributed_20260301-020134/aggregate_summary.json`
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-015615.json`
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-020134.json`
- Synced distributed winner summaries into PocketBase `champions` collection (`objective=distributed_<run_id>`).
- Synced discovery artifacts to PocketBase after patching:
  - `sim/pocketbase_client.py` (richer HTTP error details)
  - `scripts/pocketbase/sync_discovery.py` (non-zero seed for `eval_runs` records).
- Terminated all distributed worker instances after result collection to control spend.
- Added AWS operational doc:
  - `research_logs/2026-03-01_aws_distributed_runbook.md`.

## 2026-03-01 02:21:11 PST

- Ran third high-volume distributed EC2 batch:
  - run id: `20260301-021037`
  - 12x `c7i.large`
  - `n_matches=250`
  - scenarios: 216
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 212
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 4
- Collected and stored:
  - `research_logs/experiment_outputs/distributed_20260301-021037/aggregate_summary.json`
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-021037.json`
  - `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
- Synced distributed run `20260301-021037` champion summary to PocketBase.
- Combined distributed confidence summary:
  - total scenarios across runs `20260301-015615`, `20260301-020134`, `20260301-021037`: 648
  - champion win count for `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 571
- Terminated all worker instances from run `20260301-021037` after collection.

## 2026-03-01 02:23:00 PST

- Added continuous orchestration script for repeated EC2 cycles:
  - `scripts/aws/continuous_distributed_loop.sh`
- Purpose:
  - launch distributed run
  - wait for S3 shard completion
  - collect aggregate summary
  - optional PocketBase sync
  - terminate workers
  - repeat for N cycles or until epoch deadline.

## 2026-03-01 02:28:54 PST

- Fixed and validated continuous loop script behavior:
  - patched S3 polling for empty-prefix safety under `set -euo pipefail`.
  - verified end-to-end one-cycle automation run:
    - run id: `20260301-022736`
    - 2 workers
    - completed:
      - launch
      - S3 completion wait
      - collect aggregate summary
      - PocketBase sync
      - worker termination
      - final `continuous loop complete` status.
- Recovered manual smoke run from earlier loop failure:
  - run id: `20260301-022349`
  - collected + synced + terminated workers.

## 2026-03-01 02:39:26 PST

- Completed full high-volume cycle using fixed `scripts/aws/continuous_distributed_loop.sh`:
  - run id: `20260301-023132`
  - 12 workers
  - `n_matches=180`
  - winner counts:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`: 206
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.099,sell_count=1`: 9
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.106,sell_count=2`: 1
- Confirmed loop script end-to-end behavior under heavier settings:
  - launch -> wait -> collect -> sync -> terminate -> complete.
- Updated high-confidence distributed master summary:
  - file: `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
  - runs included: `20260301-015615`, `20260301-020134`, `20260301-021037`, `20260301-023132`
  - total scenarios: 864
  - champion wins (`seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`): 777

## 2026-03-01 02:56:57 PST

- Added champion summary loader module:
  - `game/champion_loader.py`
  - supports distributed winner-count summaries, param-sweep candidate summaries, and profile/objective vote summaries.
- Updated API session champion flow in `game/api.py`:
  - new endpoint `POST /strategies/load_champions`
  - session state now exposes `champion_source`, `champion_loaded_at`, and `champion_summary`
  - startup attempts to load latest local summary artifact from `research_logs/experiment_outputs`.
- Updated HUD in `web/src/routes/+page.svelte`:
  - added summary-path input and `Load distributed champions` action
  - champions panel now displays champion source and load timestamp.
- Validation completed:
  - `uv run python -m unittest discover -s tests -v` -> 14/14 passing.
  - `pnpm --dir web run check` and `pnpm --dir web run build` -> passing.
- Added distributed EC2 evolutionary search pipeline:
  - `research_logs/experiment_inputs/evolution_jobs_20260301.txt`
  - `scripts/aws/launch_evolution_experiments.sh`
  - `scripts/aws/collect_evolution_results.py`
- Uploaded fresh code artifact to S3:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_worktree_20260301-025534.tar.gz`.
- Launched 12-worker EC2 evolution run:
  - run id: `20260301-025553`
  - mapping file: `research_logs/aws_evolution_worker_map_20260301-025553.jsonl`.
- Param sweep run `20260301-024646` remains running concurrently.

## 2026-03-01 03:04:55 PST

- Collected completed EC2 evolution runs:
  - quick run `20260301-025732` -> `research_logs/experiment_outputs/evolution_20260301-025732/aggregate_summary.json`
  - high-volume run `20260301-025553` -> `research_logs/experiment_outputs/evolution_20260301-025553/aggregate_summary.json`
  - generated candidate pools:
    - `research_logs/experiment_inputs/evolution_candidate_pool_20260301-025732.txt`
    - `research_logs/experiment_inputs/evolution_candidate_pool_20260301-025553.txt`
- Collected completed param sweep run `20260301-024646`:
  - artifact: `research_logs/experiment_outputs/param_sweep_20260301-024646/aggregate_summary.json`
  - top candidate vs prior champion:
    - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`
    - mean delta vs prior champion: `+19.424` over 108 scenarios (wins: 95, losses: 13).
- Built merged evolution candidate input:
  - `research_logs/experiment_inputs/evolution_candidate_merge_20260301.txt` (24 specs).
- Terminated completed EC2 runs to control spend:
  - evolution runs `20260301-025732`, `20260301-025553`
  - param sweep run `20260301-024646`.
- Added top param-sweep candidates into API recompute candidate pool:
  - `game/api.py` discovery set now includes reserve-floor `0.06` variants.
- Started fresh distributed validation run with new candidates in tournament pool:
  - script update: `scripts/aws/launch_distributed_experiments.sh`
  - artifact uploaded: `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_worktree_20260301-030349.tar.gz`
  - run id: `20260301-030400`
  - mapping file: `research_logs/aws_worker_map_20260301-030400.jsonl`.

## 2026-03-01 03:15:07 PST

- Completed distributed upgrade validation run `20260301-030400` (12x `c7i.large`, `n_matches=180`, 216 scenarios).
- Collected artifact:
  - `research_logs/experiment_outputs/distributed_20260301-030400/aggregate_summary.json`.
- Winner counts in expanded strategy pool:
  - `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`: 105
  - `seller_extraction:opportunistic_delta=3600,reserve_bid_floor=0.06,sell_count=2`: 105
  - old champion `reserve_bid_floor=0.086`: 4
  - `reserve_bid_floor=0.099,sell_count=1`: 2
- Generated per-profile fallback mapping and recommended objective champions:
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-030400.json`
  - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-030400.json`.
- Updated champion loader precedence:
  - now supports `recommended_session_champions` payloads
  - now checks `distributed_upgrade_validation_*.json` first.
- Session startup now loads latest recommended champions automatically:
  - `ev` and `first_place` -> `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.06,sell_count=2`
  - `robustness` -> `seller_extraction:opportunistic_delta=3600,reserve_bid_floor=0.06,sell_count=2`.
- Terminated EC2 run `20260301-030400` instances after collection.
