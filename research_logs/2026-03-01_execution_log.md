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

## 2026-03-01 03:51:28 PST

- Added custom strategy-pool support to distributed launcher:
  - `scripts/aws/launch_distributed_experiments.sh` now accepts `--strategies-file`.
- Created expanded distributed pool file:
  - `research_logs/experiment_inputs/distributed_upgrade_pool_20260301.txt`.
- Launched expanded distributed validation run:
  - run id: `20260301-031824`
  - 12x `c7i.large`
  - `n_matches=240`
  - mapping file: `research_logs/aws_worker_map_20260301-031824.jsonl`
  - collected artifact: `research_logs/experiment_outputs/distributed_20260301-031824/aggregate_summary.json`
  - key winner counts:
    - `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`: 90
    - `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`: 43
- Generated profile-level winner map for `20260301-031824`:
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-031824.json`.
- Created targeted confirmation candidate set:
  - `research_logs/experiment_inputs/param_sweep_specs_targeted_20260301.txt`.
- Launched targeted EC2 param-sweep confirmation run:
  - run id: `20260301-033100`
  - 11x `c7i.large`
  - `n_matches=180`
  - champion fixed: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
  - mapping file: `research_logs/aws_param_sweep_worker_map_20260301-033100.jsonl`
  - collected artifact: `research_logs/experiment_outputs/param_sweep_20260301-033100/aggregate_summary.json`
  - result: no challenger achieved positive mean delta vs champion;
    best challenger `5400/0.032/2` at mean delta `-1.475`.
- Emitted updated session champion recommendation artifact:
  - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-033100.json`.
- Session auto-load now resolves this latest artifact and recommends:
  - `ev`, `first_place`, `robustness` => `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`.
- Terminated all EC2 worker instances for runs `20260301-031824` and `20260301-033100` after collection.

## 2026-03-01 03:55:25 PST

- Provisioned new key-accessible PocketBase EC2 node via AWS CLI:
  - instance id: `i-0854d429f873e6c52`
  - URL: `http://3.236.115.133:8090`
  - script: `scripts/aws/provision_pocketbase_ec2.sh`.
- Bootstrapped superuser and schema on new node:
  - superuser created (local ops account)
  - applied collections with `scripts/pocketbase/apply_collections.py`.
- Synced latest artifacts into new PocketBase database:
  - `scripts/pocketbase/sync_discovery.py` (strategies/champions/eval runs)
  - `scripts/aws/collect_distributed_results.py` for run `20260301-031824` with DB sync
  - `scripts/aws/collect_param_sweep_results.py` for run `20260301-033100` with DB sync.
- Verified DB records:
  - `champions` records include objectives `distributed_20260301-031824` and `param_sweep_20260301-033100`.

## 2026-03-01 04:30:25 PST

- Derived 10-game specific confirmation artifact from targeted sweep `20260301-033100`:
  - `research_logs/experiment_outputs/horizon10_confirmation_20260301-033100.json`.
- Horizon-10 signal:
  - primary champion `3300/0.029/2` remains strongest overall across objectives in targeted sweep,
  - challenger `5400/0.032/2` shows only narrow robustness-focused advantage slices and remains negative overall vs champion.
- Provisioned optional extra head-to-head run `20260301-035736` (very high `n_matches=420`) and terminated early to avoid low-yield EC2 burn after no uploads for extended runtime.

## 2026-03-01 04:32:25 PST

- Added day-of utility script:
  - `scripts/print_latest_champions.py` prints resolved champions from latest artifacts.
- Added quick operator card:
  - `research_logs/2026-03-01_quick_reference_card.md`.
- Fixed champion artifact resolution precedence bug:
  - `game/champion_loader.py` now respects pattern priority order (upgrade-validation artifacts first),
    instead of picking whichever summary file has latest mtime.
- Added regression test:
  - `test_find_latest_summary_path_respects_pattern_priority` in `tests/test_champion_loader.py`.
- Validation:
  - `uv run python -m unittest discover -s tests -v` -> 16/16 passing.
  - `scripts/print_latest_champions.py` resolves to
    `distributed_upgrade_validation_20260301-033100.json` with champion `3300/0.029/2`.

## 2026-03-01 04:49:45 PST

- Hardened evolutionary evaluator in `scripts/evolve_population.py`:
  - added baseline controls (`--baseline-file`, `--baseline-spec`, `--replace-default-baseline`),
  - changed candidate evaluation to guaranteed-in-table matches via `run_match` so candidates cannot disappear from leaderboard sampling,
  - emitted `baseline_pool` in summary artifacts.
- Added focused baseline and jobs for champion-aware search:
  - `research_logs/experiment_inputs/evolution_baseline_20260301-0447.txt`
  - `research_logs/experiment_inputs/evolution_jobs_20260301_0447.txt`
- Added utility script to build distributed validation pools from evolution artifacts:
  - `scripts/aws/build_strategy_pool.py`.
- Built and uploaded fresh worktree artifact:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_worktree_20260301-044700.tar.gz`.
- Launched new EC2 evolution fleet:
  - run id: `20260301-044713`
  - 18x `c7i.large`
  - mapping file: `research_logs/aws_evolution_worker_map_20260301-044713.jsonl`
  - objectives/profiles include 10-game focused sweeps plus correlated variants.
- Started live S3 completion monitor for run `20260301-044713` (`54` expected files).

## 2026-03-01 05:10:32 PST

- Collected and synced focused evolution run `20260301-044713`:
  - aggregate: `research_logs/experiment_outputs/evolution_20260301-044713/aggregate_summary.json`
  - candidate pool: `research_logs/experiment_inputs/evolution_candidate_pool_20260301-044713.txt`
  - PocketBase sync complete (`champions` objective `evolution_20260301-044713`).
- Built evolution-driven distributed validation pool:
  - `research_logs/experiment_inputs/distributed_upgrade_pool_20260301-0456.txt` (27 strategies).
- Launched and collected distributed run `20260301-045734` (14x `c7i.large`, `n_matches=240`), then terminated workers.
  - aggregate: `research_logs/experiment_outputs/distributed_20260301-045734/aggregate_summary.json`
  - auto-summary artifacts:
    - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-045734.json`
    - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-045734.json`
- Added automation script:
  - `scripts/aws/summarize_distributed_champions.py` to generate both distributed summary artifacts from aggregate output.
- Safety update:
  - `summarize_distributed_champions.py` now defaults to writing non-promoting candidate upgrade files,
    requiring explicit `--promote-upgrade` to produce `distributed_upgrade_validation_<run_id>.json`.
- Current stable HUD recommendation remains `3300/0.029/2`:
  - latest promoted artifact still `distributed_upgrade_validation_20260301-043312.json`.
- Param sweep incident and recovery:
  - first launch `20260301-050045` failed because candidate specs file was missing from artifact,
  - terminated failed fleet,
  - rebuilt/uploaded artifact `soldem_worktree_20260301-050705.tar.gz`,
  - relaunched as `20260301-050721` and resumed monitoring.

## 2026-03-01 05:26:05 PST

- Completed corrected EC2 param sweep run `20260301-050721` (16x `c7i.large`, 16 candidates, `n_matches=160`) against champion `3300/0.029/2`.
  - aggregate: `research_logs/experiment_outputs/param_sweep_20260301-050721/aggregate_summary.json`
  - top challenger:
    - `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
    - mean delta vs champion: `+5.133`
    - wins/losses: `77/31` over 108 scenarios.
- Extracted horizon-10 confirmation from per-scenario rows:
  - artifact: `research_logs/experiment_outputs/horizon10_confirmation_20260301-050721.json`
  - `4400/0.02/2` horizon-10 mean delta: `+8.031` (`30/6` wins/losses).
- Promoted new session champion artifact:
  - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-050721.json`
  - objective recommendations set to `4400/0.02/2` for `ev`, `first_place`, `robustness`.
- Synced promotion evidence to PocketBase (`champions` records with objective prefix `promotion_20260301-050721_*`).
- Updated code defaults and discovery pools toward promoted strategy:
  - `game/api.py` default champion and advisor fallback now `4400/0.02/2`.
  - `DISCOVERY_STRATEGY_SPECS` expanded with new top challengers (`4400/0.02/2`, `4500/0.02/2`, `2600/0.023/2`).
  - `scripts/aws/launch_distributed_experiments.sh` default pool updated to include new promoted strategy and strongest challengers.
- Terminated all worker instances for `20260301-050721` and verified no active `soldem-dist|soldem-evolution|soldem-param-sweep` EC2 workers remain.

## 2026-03-01 06:26:08 PST

- Built and uploaded fresh artifact for final morning validation:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v5_6456979_20260301-061214.tar.gz`.
- Launched human-focused distributed run `20260301-061228`:
  - 18x `c7i.large`
  - `n_matches=360`
  - strategy pool file:
    - `research_logs/experiment_inputs/distributed_confirm_pool_humanplus_20260301-0614.txt`
  - worker map:
    - `research_logs/aws_worker_map_20260301-061228.jsonl`
- Collected outputs and generated artifacts:
  - `research_logs/experiment_outputs/distributed_20260301-061228/aggregate_summary.json`
  - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-061228.json`
  - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-061228.json`
- Added stronger distributed objective analytics:
  - `scripts/aws/summarize_distributed_champions.py` now emits `objective_strength` with:
    - mean rank-points champions,
    - normalized win-margin champions.
- Created merged human-run aggregate and promoted combined artifact:
  - merged source runs:
    - `distributed_20260301-053816`
    - `distributed_20260301-061228`
  - merged aggregate:
    - `research_logs/experiment_outputs/distributed_20260301-062400-merged/aggregate_summary.json`
  - promoted summary:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-062400-merged.json`
  - promoted objective split:
    - `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
    - `first_place`: `seller_profit`
    - `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- Added day-of fast patch helper script:
  - `scripts/day_of/apply_rule_variation.py`
  - applies profile overrides, optionally recomputes champions, and prints session state in one command.
- Updated docs to current promoted state:
  - `research_logs/2026-03-01_human_playbook.md`
  - `research_logs/2026-03-01_quick_reference_card.md`
  - `research_logs/2026-03-01_system_summary.md`
  - `research_logs/2026-03-01_aws_distributed_runbook.md`
  - `research_logs/2026-03-01_day_of_patch_guide.md`
- Terminated all worker instances from run `20260301-061228` after collection.

## 2026-03-01 06:46:42 PST

- Started additional pre-7am validation to test whether `5400/0.032/2` EV promotion is stable under param-sweep settings.
- Uploaded artifact:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v5_3b8befb_20260301-062624.tar.gz`
- Launched param sweep run `20260301-062640` (`n_matches=140`, 16x workers) against champion `5400/0.032/2`.
- Terminated run `20260301-062640` early due wall-clock risk before 7:00 AM and relaunched reduced sweep:
  - run `20260301-063621` (`n_matches=50`, 16x workers)
  - mapping file: `research_logs/aws_param_sweep_worker_map_20260301-063621.jsonl`
- Collected reduced sweep output:
  - `research_logs/experiment_outputs/param_sweep_20260301-063621/aggregate_summary.json`
- Key result vs champion `5400/0.032/2`:
  - positive mean-delta challengers include:
    - `seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2` (`+3.787`)
    - `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2` (`+2.277`)
- Conservative pre-7am promotion applied:
  - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`
  - objective split:
    - `ev`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
    - `first_place`: `seller_profit`
    - `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- Verified resolver points to this latest safe artifact:
  - `uv run python scripts/print_latest_champions.py`
- Terminated all workers from run `20260301-063621` after collection.

## 2026-03-01 06:56:11 PST

- Uploaded fresh artifact for final pre-7am distributed confirmation:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v5_47149fd_20260301-064642.tar.gz`
- Launched and collected distributed run `20260301-064700`:
  - 16x `c7i.large`
  - `n_matches=120`
  - mapping file:
    - `research_logs/aws_worker_map_20260301-064700.jsonl`
  - collected outputs:
    - `research_logs/experiment_outputs/distributed_20260301-064700/aggregate_summary.json`
    - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-064700.json`
    - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-064700.json`
- Key run signal:
  - winner-count recommendation:
    - `ev`: `5400/0.032/2`
    - `first_place`: `adaptive_profile`
    - `robustness`: `4400/0.02/2`
  - objective-strength and merged multi-run evidence still favor `seller_profit` for first-place.
- Built merged aggregate across three human-focused distributed runs:
  - source runs: `053816`, `061228`, `064700`
  - merged aggregate:
    - `research_logs/experiment_outputs/distributed_20260301-065230-merged3/aggregate_summary.json`
  - promoted final artifact:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-065230-merged3.json`
  - final objective split:
    - `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
    - `first_place`: `seller_profit`
    - `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- Verified resolver now points to merged3 artifact via:
  - `uv run python scripts/print_latest_champions.py`
- Terminated all workers from run `20260301-064700` after collection.

## 2026-03-01 06:55:28 PST

- Added day-of mode-switch policy doc:
  - `research_logs/2026-03-01_mode_switch_policy.md`
  - defines trigger rules for aggressive merged3 mode vs conservative safe fallback.
- Linked mode-switch doc from pre-7am handoff summary:
  - `research_logs/2026-03-01_pre7am_summary.md`
- Final state check:
  - no active `soldem-dist|soldem-evolution|soldem-param-sweep` EC2 instances
  - latest resolver artifact:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-065230-merged3.json`

## 2026-03-01 06:59:48 PST

- Final pre-7am timestamp checkpoint recorded.
- Confirmed active promotion remains:
  - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-065230-merged3.json`
  - objective split:
    - `ev`: `5400/0.032/2`
    - `first_place`: `seller_profit`
    - `robustness`: `4400/0.02/2`
- Reconfirmed no active simulation workers in EC2.

## 2026-03-01 07:10:28 PST

- Continued post-cutoff EC2 validation cycle.
- Uploaded artifact:
  - `s3://soldem-2026-539881456097-1772358537/artifacts/soldem_v5_751cce5_20260301-070153.tar.gz`
- Launched and collected distributed run `20260301-070229`:
  - 16x `c7i.large`
  - `n_matches=150`
  - outputs:
    - `research_logs/experiment_outputs/distributed_20260301-070229/aggregate_summary.json`
    - `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-070229.json`
    - `research_logs/experiment_outputs/upgrade_validation_candidate_20260301-070229.json`
- Built merged aggregate across four human-focused distributed runs:
  - source runs: `053816`, `061228`, `064700`, `070229`
  - merged aggregate:
    - `research_logs/experiment_outputs/distributed_20260301-071000-merged4/aggregate_summary.json`
  - promoted artifact:
    - `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-071000-merged4.json`
  - promoted objective split:
    - `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
    - `first_place`: `seller_profit`
    - `robustness`: `seller_extraction:opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2`
- Added post-cutoff handoff note:
  - `research_logs/2026-03-01_post7am_update.md`
- Verified no active EC2 simulation workers after termination.
