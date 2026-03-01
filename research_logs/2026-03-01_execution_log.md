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
