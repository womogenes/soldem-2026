# Sold 'Em research log

Local timestamp: 2026-03-01 01:45:00 PST

## 01:28 PST
- Audited `RULES.md`, engine flow, ranking utilities, strategy loader, simulator, API, and HUD.
- Confirmed existing plugin strategy format (`load_strategy`) and compact JSONL game logging.
- Verified baseline unit tests pass with `uv run python -m unittest discover -s tests -q`.

## 01:44 PST
- Ran baseline population sweeps across objectives and correlation modes (`research_logs/experiment_outputs/baseline_*.json`).
- Verified 50-card hand combinatorics exactly (`2,118,760` combinations), confirming `CATEGORY_RARITY_COUNTS_50` and rarity ordering implementation.
- Added strategy families in `strategies/builtin.py`: `market_maker`, `conservative_ultra`, `elastic_conservative`, `conservative_plus`, `mc_edge`.
- Ran candidate sweeps (`research_logs/experiment_outputs/candidates_*.json`): `market_maker` won EV in all 12 objective/correlation runs.
- Ran horizon/correlation matrix (`research_logs/experiment_outputs/horizon_correlation_matrix.json`): `market_maker` won 25/27 cells; `conservative_ultra` won 2 robustness-heavy cells.
- Ran rule-variant matrix (`research_logs/experiment_outputs/rule_variant_matrix.json`): `market_maker` won 14/18 profile/objective cells; robustness fallback usually `conservative_ultra`.
- Updated API default champions in `game/api.py` to `market_maker` (`ev`, `first_place`) and `conservative_ultra` (`robustness`).
- Provisioned PocketBase on AWS EC2 (`i-08f41ea7a4d11aaca`, `44.221.42.217`) and created superuser.
- Added PocketBase automation scripts: `scripts/pocketbase_bootstrap.py`, `scripts/sync_experiments_to_pocketbase.py`.
- Synced candidate experiment outputs to PocketBase and verified records in `strategies`, `eval_runs`, `champions`, and `match_results`.
- Added day-of operations docs in `docs/` and literature review in `research_logs/literature_auction_poker_imperfect_info_2026-03-01.md`.


## 01:47 PST
- Added `scripts/apply_rule_patch.py` and `scripts/precompute_variants.py` for fast day-of operations.
- Added docs in `docs/`: `rule_assumptions.md`, `strategy_format.md`, `cloud_setup.md`, `day_of_runbook.md`, `day_of_patch_guide.md`, `champion_results.md`.
- Added minimal external strategy template at `strategies/examples/minimal_strategy.py`.
- Validated web checks with `pnpm --dir web check` and `pnpm --dir web build`.
- Performed API E2E smoke checks on `/health`, `/session/state`, and `/advisor/recommend`; default strategy resolves to `market_maker`.
- Extended tests in `tests/test_sim_runner.py` for new strategy tags and match smoke.
- Terminated redundant EC2 instance `i-0c4e23958644122b7` to reduce spend.

## 03:15 PST
- Read `../v2/research_logs/000_god_prompt.md` again and continued iterative strategy search.
- Added new strategy variants in `strategies/builtin.py`: `market_maker_tight`, `market_maker_aggr`, `regime_switch`, `regime_switch_robust`.
- Ran medium candidate sweep (`candidate2_*.json`) and selected finalists.
- Added `scripts/run_long_validation.py` and ran long matrix in parallel by objective:
  - 3 seeds x 3 horizons x 4 correlation modes x 3 objectives
  - 450 matches per cell
  - Outputs: `long_validation_ev.json`, `long_validation_first_place.json`, `long_validation_robustness.json`
- Long-matrix result:
  - `market_maker_tight` won all EV cells (`12/12`) and first-place cells (`12/12`).
  - `regime_switch_robust` won all robustness cells (`12/12`).
- Added `scripts/run_rule_profile_validation.py` and ran long rule-profile matrix:
  - 6 profiles x 3 objectives x 3 seeds, 320 matches per seed/cell
  - Output: `rule_profile_validation_long.json`
- Rule-profile result: `market_maker_tight` for EV/first-place and `regime_switch_robust` for robustness in all profiles.
- Updated `game/api.py` profile defaults to the new champion map.
- Updated docs and handoff files (`docs/day_of_runbook.md`, `docs/day_of_patch_guide.md`, `docs/champion_results.md`, `research_logs/2026-03-01_7am_handoff_summary.md`) with high-confidence recommendations.
- Extended literature doc with additional 2025-2026 primary sources and updated implications.

## 03:25 PST
- Added `scripts/run_rule_profile_validation.py` and completed 54-run profile matrix at 320 matches per seed/cell.
- Confirmed champion map is stable across all tested profiles:
  - `market_maker_tight` for `ev` and `first_place`
  - `regime_switch_robust` for `robustness`
- Updated `PROFILE_OBJECTIVE_DEFAULTS` in `game/api.py` to new champion map.
- Added `research_logs/champion_lookup_from_rule_profile_validation_long.json` and updated fallback docs.
- Extended `scripts/sync_experiments_to_pocketbase.py` to ingest multi-run files (`long_validation_*`, `rule_profile_validation_long`).
- Synced new long-run outputs to PocketBase; DB totals now:
  - strategies: 16
  - eval_runs: 184
  - champions: 183
  - match_results: 2002

## 03:45 PST
- Ran additional extreme-correlation stress matrix (`correlation_stress_matrix.json`):
  - objectives `ev,first_place,robustness`
  - strengths `0.35,0.5,0.7`
  - modes `respect,herd,kingmaker`
  - adversarial pair structures
  - total 81 scenarios
- Stress winners by EV: `market_maker_tight` 50/81, `regime_switch_robust` 23/81.
- Fixed objective-selection bug in validation scripts:
  - `scripts/run_long_validation.py` and `scripts/run_rule_profile_validation.py` now rank by objective-appropriate metric in `summary.top`.
- Rewrote existing validation summaries to corrected format and regenerated champion lookup artifacts.
- Added `correlation_stress_summary.json` and updated docs to distinguish safe defaults from high-variance first-place overrides.

## 03:52 PST
- Synced `correlation_stress_matrix.json` to PocketBase after extending sync tooling for list-based matrix artifacts.
- Current PocketBase totals:
  - strategies: 16
  - eval_runs: 265
  - champions: 264
  - match_results: 2893
- Confirmed stress-test takeaway remains unchanged for safe play:
  - EV-safe default: `market_maker_tight`
  - robustness-safe default: `regime_switch_robust`
  - optional high-variance first-place override: `pot_fraction`
