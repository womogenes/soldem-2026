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

## 2026-03-01 02:16:18 PST

- Re-read `research_logs/000_god_prompt.md` to align continuation scope.
- Added dynamic table-read inference and strategy adaptation in API:
  - infers modes: `balanced`, `aggressive`, `passive`, `correlated_pair`, `competitive`
  - computes confidence and summary metrics from in-session events
  - outputs `table_read` and `recommended_preset` in session state
  - uses mode-aware champion resolution (objective + profile + observed table behavior)
- Updated HUD:
  - event logging now includes `seller_idx`
  - displays `table_read` and `recommended_preset`
  - added `Use auto table read preset` action
- Added tests for dynamic behavior in `tests/test_api_session.py`.
- Launched and completed extended hero benchmark suite v2 (`27` scenarios):
  - artifacts: `research_logs/experiment_outputs/hero_suite_v2/*.json`
  - pool-level winners:
    - mixed pool: `equity_sniper_ultra` 6/9, `conservative_plus` 3/9
    - shark pool: `equity_sniper_ultra` 9/9
    - chaos pool: `conservative_plus` 9/9
  - aggregate means across all v2 scenarios:
    - `conservative_plus`: EV 92.76, first 0.403, p10 -1.11
    - `equity_sniper_ultra`: EV 89.61, first 0.389, p10 -13.11
- Interpretation:
  - retain `conservative_plus` as robust default under chaotic/erratic fields
  - switch to `equity_sniper_ultra` when table reads as competitive/tight or correlated

## 2026-03-01 02:23:48 PST

- Added simulation-native adaptive strategy `meta_switch` in `strategies/builtin.py` for controlled switching between conservative/sniper/risk-on delegates.
- Ran dedicated meta benchmark suite (`18` scenarios):
  - artifacts: `research_logs/experiment_outputs/meta_suite/*.json`
  - overall winner frequency: `conservative_plus` 10, `equity_sniper_ultra` 8, `meta_switch` 0
  - aggregate means:
    - `conservative_plus`: EV 92.44, first 0.392, p10 +1.22
    - `equity_sniper_ultra`: EV 92.10, first 0.396, p10 -12.11
    - `meta_switch`: EV 82.36, first 0.455, p10 -54.89
- Decision:
  - keep `meta_switch` as experimental high-variance fallback only (not default champion).
  - maintain current primary pair (`conservative_plus`, `equity_sniper_ultra`) for day-of play.
- Improved PocketBase seeding idempotency:
  - `scripts/seed_pocketbase.py` now avoids duplicate `eval_runs` by status.

## 2026-03-01 02:24:54 PST

- Added human execution drill guide:
  - `research_logs/005_human_training_drills.md`
- Focus areas:
  - sub-10-second decision workflow,
  - objective-switch discipline,
  - table-read adaptation rehearsal,
  - anti-tilt guardrails.

## 2026-03-01 02:47:05 PST

- Added rule-override support in simulation runner (`sim/runner.py`) so experiments can benchmark arbitrary announced variants without adding static profiles first.
- Added new day-of solver scripts:
  - `scripts/quick_variant_solver.py` (population-style, corrected objective metric mapping)
  - `scripts/quick_variant_hero_solver.py` (hero-vs-mixed-pool methodology)
- Ran `quick_variant_suite_v2` and `quick_variant_hero_suite_v3` artifacts to build profile-conditioned strategy lookup references.
- Added expanded `meta_switch` evaluation (`meta_suite_v2`) including mixed/shark/chaos pools and robustness objective.
- Key takeaway from newest aggregate (`meta_suite_v2`):
  - `conservative_plus` remains strongest robust EV baseline (best mean EV and best p10 tail among tested finalists).
  - `equity_sniper_ultra` remains strongest competitive/correlation upside option.
  - `meta_switch` improves first-place pressure in some setups but underperforms baseline EV robustness; keep as optional mode only.
- Added API endpoint `POST /strategies/set_champions` and manual lock mode:
  - supports explicit champion overrides.
  - `dynamic_resolution_enabled=false` locks manual champion map.
- Updated patch workflow script `scripts/day_of_patch.py`:
  - supports `--set-ev`, `--set-first-place`, `--set-robustness`.
  - supports `--keep-dynamic` to avoid locking when desired.
- UI now displays `dynamic_resolution_enabled` to avoid ambiguity during live operation.
- Revalidated end-to-end:
  - backend tests: 12/12 pass
  - frontend check/build: pass

## 2026-03-01 02:48:20 PST

- Produced variant lookup artifact:
  - `research_logs/006_variant_lookup_table.md`
- This lookup is generated from hero-vs-mixed-pool solver outputs in `quick_variant_hero_suite_v3` and is intended for rapid manual champion locking via `scripts/day_of_patch.py`.
- Added explicit caution that `pot_fraction` can win short-stack first-place races but remains high downside risk in broader fields.

## 2026-03-01 02:49:43 PST

- Validated PocketBase worker heartbeat pipeline end-to-end using `scripts/worker_heartbeat.py`.
- Created smoke worker record:
  - worker_id: `local-smoke-1`
  - status: `alive`
  - role: `sim`
- Verified record is queryable in `workers` collection.

## 2026-03-01 03:06:00 PST

- Added evolutionary random-search script over `EquityAwareStrategy` parameter family:
  - `scripts/evolve_equity_family.py`
- Conducted search and candidate validation:
  - search outputs: `research_logs/experiment_outputs/evolve_equity_results_v2.json`
  - strongest candidate identified: `equity_auto_023`.
- Cross-validation runs:
  - head-to-head suite: `research_logs/experiment_outputs/evolve_head2head/*.json`
  - broader candidate suite: `research_logs/experiment_outputs/evolve_candidate_suite/*.json`
- Aggregate signal:
  - `equity_auto_023` beats current champions in most mixed/shark scenarios and remains positive-tail in chaos.
  - overall means from evolved candidate suite:
    - `equity_auto_023`: EV 99.44, first 0.458, p10 +11.67
    - `conservative_plus`: EV 90.21, first 0.393, p10 -4.89
    - `equity_sniper_ultra`: EV 90.19, first 0.420, p10 -8.00
- Promoted evolved candidate into built-ins as `equity_evolved_v1`.
- Updated runtime policy:
  - `first_place` champion default now `equity_evolved_v1`
  - competitive/correlated and variant-biased modes now route to `equity_evolved_v1`
  - aggressive/chaotic mode still routes to `conservative_plus`
- Added manual champion lock support and visibility:
  - API endpoint `POST /strategies/set_champions`
  - `day_of_patch.py` flags: `--set-ev`, `--set-first-place`, `--set-robustness`, `--keep-dynamic`
  - HUD displays `dynamic_resolution_enabled`
- Revalidated after promotion:
  - backend tests: 12/12 pass
  - frontend check/build: pass

## 2026-03-01 03:07:51 PST

- Improved `scripts/seed_pocketbase.py` to update existing strategy records (family/commit/params), not just create missing ones.
- Synced PocketBase after evolved-strategy promotion:
  - strategies_seeded: 0
  - strategies_updated: 17
  - champions: `ev=conservative_plus`, `first_place=equity_evolved_v1`, `robustness=conservative_plus`
