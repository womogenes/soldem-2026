# Night rollout log

Local time: 2026-03-01 01:25:02 PST

## Scope

- Maximize day-of performance for Sold 'Em.
- Keep a timestamped trail of research, simulation runs, and integration changes.
- Use `research_logs/000_god_prompt.md` as the governing spec for rollout continuity.

## 2026-03-01 01:25:02 PST

- Loaded and verified `RULES.md`, `game/engine_base.py`, `game/rules.py`, `game/utils.py`, and the existing simulation/HUD pipeline.
- Verified all current tests pass with `uv run -m unittest discover -s tests -v`.
- Exhaustively enumerated all 2,118,760 five-card combinations from the 50-card deck to validate rarity counts:
  - five_kind: 10
  - straight_flush: 30
  - flush: 1230
  - four_kind: 2250
  - full_house: 9000
  - straight: 18720
  - three_kind: 90000
  - two_pair: 180000
  - high_card: 767520
  - one_pair: 1050000
- Conclusion: current `rarity_50` ordering in `game/utils.py` matches exact combinatorics.

## Next actions

- Run baseline experiment matrix on current strategy set.
- Add stronger strategy family oriented around marginal showdown equity and auction EV.
- Run evolutionary/tournament search under correlated-human models.
- Integrate best strategy defaults and actionable outputs into HUD/API.
- Add day-of fast patch guide for rule variations.

## 2026-03-01 01:28:02 PST

- Added new strategy family in `strategies/builtin.py`:
  - `equity_balanced`
  - `equity_sniper`
  - `equity_harvest`
  - `house_hammer`
- New family behavior:
  - Dynamic bid sizing from marginal hand delta, pot size, orbit urgency, stack pressure, and observed opponent aggression.
  - Seller card selection based on market appeal minus self-hand preservation cost.
  - Distinct variants for balanced play, low-volatility sniping, extraction-heavy selling, and house-auction emphasis.
- Re-ran full test suite (`uv run -m unittest discover -s tests -v`): all tests pass.

## 2026-03-01 01:30:56 PST

- Baseline+new-strategy matrix (`81` scenario rows, `n_matches=30`) completed at `research_logs/experiment_outputs/with_equity_small/matrix_results.json`.
- Scenario winners count:
  - conservative: 54
  - equity_sniper: 23
  - house_hammer: 3
  - equity_harvest: 1
- Added second strategy iteration:
  - `conservative_plus`
  - `equity_sniper_plus`
  - `equity_sniper_ultra`
  - `equity_flex`
- Tests remain green after iteration.

## 2026-03-01 01:45:23 PST

- Completed iterative strategy search with expanded pool and scenario matrices.
- Iteration-2 matrix (`research_logs/experiment_outputs/iter2_small/matrix_results.json`) winner frequencies across 81 scenarios:
  - `equity_sniper_ultra`: 30
  - `conservative_plus`: 25
  - `equity_sniper`: 15
  - `conservative`: 6
- Added `scripts/benchmark_hero.py` to evaluate a designated hero strategy against randomized opponent pools with fair seat randomization.
- Hero suite completed (`research_logs/experiment_outputs/hero_suite/*.json`) with mixed-human opponent pool:
  - Scenario winners: `conservative_plus` in 6/8, `equity_sniper_ultra` in 2/8.
  - Overall cross-scenario means:
    - `conservative_plus`: EV 59.12, first-place 0.239, p10 -30.25
    - `equity_sniper_ultra`: EV 57.17, first-place 0.251, p10 -34.25
- Rule-profile checks (`research_logs/experiment_outputs/rule_profiles/*.json`):
  - `high_low_split` / `seller_self_bid`: `conservative_plus` strongest.
  - `baseline_v1` / `top2_split` / `standard_rankings` / `single_card_sell`: `equity_sniper_ultra` narrowly strongest.
- Practical recommendation at this checkpoint:
  - default EV/robustness: `conservative_plus`
  - first-place upside and correlation-heavy tables: `equity_sniper_ultra`
  - high-variance exploit mode (soft table): `pot_fraction` only as explicit risk-on option.

## 2026-03-01 01:55:18 PST

- Provisioned PocketBase on EC2 with script:
  - instance_id: `i-0214ea32290cb6b1a`
  - public_ip: `18.204.1.6`
  - URL: `http://18.204.1.6:8090`
- Enabled access and bootstrapped superuser via EC2 Instance Connect + remote CLI.
- Added automation scripts:
  - `scripts/sync_pocketbase_schema.py` for collection/field synchronization from `infra/pocketbase_collections.json`.
  - `scripts/seed_pocketbase.py` for seeding strategies, champions, and eval run metadata from local experiment artifacts.
- Synced schema and seeded records successfully:
  - strategies: 15
  - champions: 3
  - eval_runs: 4
- Noted PocketBase validation quirk in this environment: required numeric fields reject `0`; seeding now uses positive non-zero values where needed.

## 2026-03-01 01:59:03 PST

- Added literature synthesis with primary-source references:
  - `research_logs/002_literature_review.md`
- Added day-of rapid patch tooling:
  - `scripts/day_of_patch.py`
  - `research_logs/003_day_of_fast_patch_guide.md`
- Updated API champion resolution to respond to active rule profile characteristics (not only profile name), including split-pot and single-card variants.
- Updated HUD with quick strategy preset controls and objective-champion one-click selection.
- Added PocketBase automation scripts and validated end-to-end:
  - `scripts/sync_pocketbase_schema.py`
  - `scripts/seed_pocketbase.py`
- Verified local quality gates after changes:
  - backend tests: pass
  - frontend `pnpm check`: pass
  - frontend production build: pass

## 2026-03-01 01:59:44 PST

- Added operator-facing handoff snapshot:
  - `research_logs/004_status_snapshot.md`
- Snapshot includes:
  - current best strategy recommendations by regime,
  - run commands for API + web HUD,
  - day-of patch command patterns,
  - PocketBase deployment status and cost-control commands.

## 2026-03-01 02:00:48 PST

- Latency smoke benchmark for advisor core (`recommend_action`, bid phase):
  - 200 calls in 0.8548s total
  - average 4.274 ms per call
- This is comfortably within the 10-second day-of turn budget, leaving room for UI interaction and manual data entry.
