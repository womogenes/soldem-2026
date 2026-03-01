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

## 2026-03-01 03:08:59 PST

- Updated variant solver defaults to include `equity_evolved_v1` in candidate sets:
  - `scripts/quick_variant_solver.py`
  - `scripts/quick_variant_hero_solver.py`
- Added fresh smoke artifacts:
  - `research_logs/experiment_outputs/quick_variant_smoke_v3.json`
  - `research_logs/experiment_outputs/quick_variant_hero_smoke_v2.json`
- Revalidated backend test suite after updates: 12/12 pass.

## 2026-03-01 03:11:25 PST

- Validated Bedrock runtime access and measured practical latency.
- Added `scripts/aws/bedrock_latency_probe.sh` (defaulting to a working inference profile ID).
- Observed latency profile for `us.anthropic.claude-3-5-haiku-20241022-v1:0`:
  - cold-ish first call can be ~6.8s
  - warm calls ~1.8-2.1s
  - 3-call average ~3.5s
- Conclusion: LLM fallback is feasible within the 10-second turn budget if prompt scope remains tight.
- Added summary doc:
  - `research_logs/007_bedrock_latency.md`

## 2026-03-01 03:13:26 PST

- Re-read `research_logs/000_god_prompt.md` and continued rollout work under the same spec.
- Verified uncommitted LLM advisor integration paths:
  - API endpoint: `POST /advisor/llm_hint`
  - UI control: `Get LLM hint`
  - backend helper module: `game/llm_advisor.py`

## 2026-03-01 03:31:12 PST

- Started broad short-horizon solver pass (`n_tables=180`) and canceled after runtime proved too high without checkpointing.
- Switched to bounded, parallel profile sweeps to keep throughput high:
  - `night_qvhs_baseline_v1_50t_seed41001.json`
  - `night_qvhs_top2_split_50t_seed41002.json`
  - `night_qvhs_high_low_split_50t_seed41003.json`
  - `night_qvhs_single_card_sell_50t_seed41004.json`
  - `night_qvhs_seller_self_bid_50t_seed41005.json`
  - `night_qvhs_standard_rankings_50t_seed41006.json`
- Aggregate winners across six built-in profiles:
  - EV: `equity_evolved_v1` won 6/6
  - robustness: `equity_evolved_v1` won 6/6
  - first-place: `equity_evolved_v1` won 4/6, `meta_switch` won 2/6

## 2026-03-01 03:37:41 PST

- Ran first-place tie-breaks with larger samples (`n_tables=150`) for the ambiguous profiles:
  - baseline: `night_qvhs_baseline_v1_first_place_150t_seed42001.json`
  - seller-self-bid: `night_qvhs_seller_self_bid_first_place_150t_seed42002.json`
- Tie-break outcome:
  - baseline first-place: `meta_switch` > `equity_evolved_v1` by ~0.013 first-place rate
  - seller-self-bid first-place: `equity_evolved_v1` > `meta_switch` by ~0.001 first-place rate
- Updated resolver policy:
  - first-place + passive/high-confidence: `pot_fraction`
  - first-place + baseline profile: `meta_switch`
  - otherwise first-place: `equity_evolved_v1`
  - EV/robustness: `equity_evolved_v1` default
- Added regression tests for new policy in `tests/test_api_session.py`.

## 2026-03-01 03:41:55 PST

- Ran targeted chaos/aggression checks to validate removing conservative default:
  - `night_aggressive_pool_check_43001.json`
  - `night_mixed_chaos_pool_check_43002.json`
- In both checks, `equity_evolved_v1` beat `conservative_plus` on EV and first-place, with better or comparable p10 tails.
- Conclusion:
  - keep `conservative_plus` as optional manual fallback only, not automatic default.

## 2026-03-01 03:47:05 PST

- Fixed stale champion seeding logic in `scripts/seed_pocketbase.py`.
- Previous issue:
  - script force-overrode champions to `first_place=equity_evolved_v1` and `robustness=conservative_plus`, ignoring latest experiments.
- New behavior:
  - reads latest profile-specific quick-variant artifacts (`night_qvhs_*`) for champion winners.
  - uses larger-sample first-place tie-break artifacts (`*_first_place_150t_*`) when available.
  - falls back to legacy `hero_suite` aggregation only if profile-specific artifacts are missing.
- Verified parser outputs:
  - baseline: `ev=equity_evolved_v1`, `first_place=meta_switch`, `robustness=equity_evolved_v1`
  - seller-self-bid: all three objectives `equity_evolved_v1`.

## 2026-03-01 03:47:49 PST

- Applied updated seeding logic to PocketBase (`http://18.204.1.6:8090`) with commit `d88b85d`.
- Result:
  - `strategies_updated`: 17
  - champion records now set to:
    - `ev=equity_evolved_v1`
    - `first_place=meta_switch`
    - `robustness=equity_evolved_v1`

## 2026-03-01 03:59:35 PST

- Ran additional weird-variant stress simulations (all at `n_tables=40`, `n_games=10`):
  - `night_weird_shortstack_mix_40t_seed51001.json`
  - `night_weird_deepstack_mix_40t_seed51002.json`
  - `night_weird_selfbid_top2_40t_seed51003.json`
  - `night_weird_std_highlow_single_40t_seed51004.json`
  - `night_weird_short_selfbid_40t_seed51005.json`
- Aggregate from this stress sample:
  - EV winners: `equity_evolved_v1` in 5/5
  - robustness winners: `equity_evolved_v1` in 5/5
  - first-place winners: `equity_evolved_v1` in 3/5, `pot_fraction` in 2/5
- Pattern detected:
  - `pot_fraction` first-place wins only under sprint-like short-stack profiles (`n_orbits<=2`, low stacks).
- Updated API resolver policy:
  - first-place objective now auto-selects `pot_fraction` when rule profile is sprint (`n_orbits<=2` and `start_chips<=150`).
  - first-place passive/high-confidence table-read fallback to `pot_fraction` remains.
- Added regression test:
  - `test_sprint_profile_first_place_prefers_pot_fraction` in `tests/test_api_session.py`.
- Added dedicated summary:
  - `research_logs/008_weird_variant_stress.md`.

## 2026-03-01 04:01:49 PST

- Hardened Bedrock hint parsing in `game/llm_advisor.py`:
  - robust JSON extraction from code-fenced or mixed-text model responses.
  - output normalization and guardrails:
    - bid clamped to `[0, stack]`
    - confidence clamped to `[0, 1]`
    - mode constrained to `{conservative, balanced, aggressive}`
    - rationale cleaned with bounded length.
- Added parser/normalization regression tests:
  - `tests/test_llm_advisor.py` (`3` tests).
- Re-ran full test suite: `19/19` passing.

## 2026-03-01 04:03:13 PST

- Added one-command day-of variant solve-and-patch helper:
  - `scripts/day_of_autosolve_patch.py`
- Behavior:
  - runs `quick_variant_hero_solver.py` with specified variant and small budget,
  - extracts objective winners,
  - applies rule profile and champion lock directly to API.
- Added `--dry-run` mode for preflight verification.
- Updated docs:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`

## 2026-03-01 04:05:48 PST

- Ran end-to-end smoke of `scripts/day_of_autosolve_patch.py` against live local API instance (`uvicorn` on `127.0.0.1:8010`).
- Confirmed one-command flow executes:
  - `POST /rules/apply_profile`
  - `POST /strategies/set_champions`
  - `GET /session/state`
- Added prior-guardrail logic to autosolve script to reduce noisy overrides at low sample sizes:
  - default priors by profile:
    - EV/robustness: `equity_evolved_v1`
    - first-place: `meta_switch` (baseline), `equity_evolved_v1` (non-baseline), `pot_fraction` (sprint profiles)
  - solver top tags are only accepted when margin exceeds thresholds (defaults):
    - `ev_gap=12.0`
    - `first_gap=0.04`
    - `robustness_gap=20.0`
  - override available with `--no-prior-guardrail`.
- Updated guide docs to include guardrail behavior and override flag.

## 2026-03-01 04:07:08 PST

- Benchmarked autosolve patch runtime using default budget:
  - command: `scripts/day_of_autosolve_patch.py --n-tables 12 --n-games 8 --dry-run`
  - measured wall-clock: `22.895s`
- This is comfortably inside the 2-minute patch requirement.

## 2026-03-01 04:11:40 PST

- Ran autosolve guardrail calibration across three profiles (`baseline_v1`, `top2_split`, sprint override) and three seeds (`53001-53003`):
  - artifacts: `research_logs/experiment_outputs/autosolve_guardrail_checks/*.json`
- Compared low-budget autosolve selections to high-confidence mapping:
  - EV: guardrailed `9/9` match vs raw solver `5/9`
  - first-place: guardrailed `8/9` match vs raw solver `5/9`
  - robustness: guardrailed `9/9` match vs raw solver `7/9`
- Added calibration summary:
  - `research_logs/009_autosolve_guardrail_calibration.md`
- Updated day-of guide to include stricter first-place margin option (`--first-gap 0.07`) when needed.

## 2026-03-01 04:12:28 PST

- Re-seeded PocketBase with latest strategy metadata commit (`8e60526`):
  - endpoint: `http://18.204.1.6:8090`
  - `strategies_updated`: 17
  - champion map remains:
    - `ev=equity_evolved_v1`
    - `first_place=meta_switch`
    - `robustness=equity_evolved_v1`

## 2026-03-01 04:13:14 PST

- Performed real Bedrock (non-dry) hint call after parser hardening:
  - model: `us.anthropic.claude-3-5-haiku-20241022-v1:0`
  - latency: `2806 ms`
  - output parsed successfully into normalized hint schema (`bid`, `confidence`, `mode`, `rationale`).
- Updated `research_logs/007_bedrock_latency.md` with this live invocation confirmation.

## 2026-03-01 04:16:37 PST

- Ran baseline first-place correlation-strength sweep using `scripts/benchmark_hero.py`:
  - artifacts: `night_corr_strength_0p00/0p20/0p35/0p50/0p70_*.json`
  - heroes: `meta_switch`, `equity_evolved_v1`, `pot_fraction`
  - objective: `first_place`
- Finding:
  - baseline first-place is mode-sensitive; `meta_switch` is not always dominant under correlated/competitive conditions.
- Updated resolver policy:
  - baseline + balanced/calm -> `meta_switch`
  - baseline + `competitive` / `correlated_pair` / `aggressive` -> `equity_evolved_v1`
  - sprint profile or passive/high-confidence first-place -> `pot_fraction`
- Updated docs:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`
  - `research_logs/006_variant_lookup_table.md`
  - new summary: `research_logs/010_correlation_strength_first_place.md`

## 2026-03-01 04:17:30 PST

- Re-seeded PocketBase after baseline first-place policy refinements:
  - commit: `2a4f136`
  - `strategies_updated`: 17
  - champion map remains:
    - `ev=equity_evolved_v1`
    - `first_place=meta_switch`
    - `robustness=equity_evolved_v1`

## 2026-03-01 04:20:23 PST

- Ran updated horizon sensitivity sweeps for latest strategy set (`5/10/20` games):
  - no-correlation artifacts:
    - `night_horizon_ev_5g_none_seed55005.json`
    - `night_horizon_ev_10g_none_seed55010.json`
    - `night_horizon_ev_20g_none_seed55020.json`
  - respect-correlation artifacts (`strength=0.35`):
    - `night_horizon_ev_5g_respect35_seed55105.json`
    - `night_horizon_ev_10g_respect35_seed55110.json`
    - `night_horizon_ev_20g_respect35_seed55120.json`
- Result:
  - `equity_evolved_v1` won EV in every tested horizon and regime.
  - no evidence from this pass that longer horizons favor reverting to `conservative_plus`.
- Added summary:
  - `research_logs/011_horizon_sensitivity.md`

## 2026-03-01 04:21:09 PST

- Re-seeded PocketBase after horizon update checkpoint:
  - commit: `ce77279`
  - `strategies_updated`: 17
  - champion map unchanged:
    - `ev=equity_evolved_v1`
    - `first_place=meta_switch`
    - `robustness=equity_evolved_v1`

## 2026-03-01 04:23:50 PST

- Added resolver explainability output in API/HUD:
  - session state now includes `resolved_champion_reasons`.
  - `/advisor/recommend` and `/advisor/llm_hint` now include `strategy_reason`.
  - HUD displays strategy reason in advisor and LLM hint panels.
- Revalidated after update:
  - backend tests: `19/19` pass
  - frontend `pnpm -C web check`: pass
  - frontend `pnpm -C web build`: pass

## 2026-03-01 04:24:34 PST

- Re-seeded PocketBase with latest checkpoint commit `fd2a462`.
- Result:
  - `strategies_updated`: 17
  - champions unchanged (`ev=evolved`, `first_place=meta_switch`, `robustness=evolved`).

## 2026-03-01 04:30:14 PST

- Ran first-place horizon sweeps (`5/10/20`) under baseline rules for:
  - no-correlation (`night_horizon_first_*_none_seed*.json`)
  - respect correlation 0.35 (`night_horizon_first_*_respect35_seed*.json`)
- Added extra seeds for ambiguous respect cases:
  - 5-game: `56105/56106/56107`
  - 10-game: `56110/56111/56112`
  - 20-game: `56120/56121/56122`
- Multi-seed respect aggregates favored `meta_switch` for baseline first-place across all horizons.
- Reverted temporary baseline dynamic-mode first-place override:
  - baseline first-place now stays `meta_switch` (except sprint/passive `pot_fraction` overrides).
- Added summary:
  - `research_logs/012_first_place_horizon_check.md`
- Updated related docs:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`
  - `research_logs/006_variant_lookup_table.md`
  - `research_logs/010_correlation_strength_first_place.md` (marked exploratory).

## 2026-03-01 04:31:17 PST

- Re-seeded PocketBase after first-place horizon updates:
  - commit: `b9fec0d`
  - `strategies_updated`: 17
  - champion map unchanged:
    - `ev=equity_evolved_v1`
    - `first_place=meta_switch`
    - `robustness=equity_evolved_v1`

## 2026-03-01 04:32:29 PST

- Tightened autosolve first-place guardrail default in `scripts/day_of_autosolve_patch.py`:
  - `first_gap`: `0.04` -> `0.07`
- Motivation:
  - reduce noisy first-place champion flips at low solver budgets.
- Updated docs:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/009_autosolve_guardrail_calibration.md`
- Verified via dry-run output that default threshold now reports `0.07`.

## 2026-03-01 04:33:27 PST

- Re-seeded PocketBase after autosolve guardrail threshold update:
  - commit: `5a0a87a`
  - `strategies_updated`: 17
  - champion map unchanged (`evolved`, `meta_switch`, `evolved`).

## 2026-03-01 04:34:17 PST

- Created rolling handoff draft for later finalization near 7 am:
  - `research_logs/013_pre7_handoff_draft.md`
- Draft includes:
  - current champion policy,
  - fast day-of commands,
  - current runtime and validation status,
  - pointers to latest supporting research docs.

## 2026-03-01 04:40:19 PST

- Ran targeted first-place evolutionary candidate screen:
  - generation run: `evolve_first_place_58001.json` (top candidate `equity_auto_034`)
  - multi-seed validation runs:
    - `night_first_candidate_baseline_none_seed59010/59012/59013.json`
    - `night_first_candidate_baseline_respect35_seed59011/59014/59015.json`
- Result:
  - candidate did not beat both incumbents (`meta_switch`, `equity_evolved_v1`) consistently.
- Decision:
  - do **not** promote new first-place candidate at this time.
  - keep current champion policy unchanged.
- Added summary:
  - `research_logs/014_first_place_candidate_screen.md`.

## 2026-03-01 04:43:32 PST

- Added day-of preflight script:
  - `scripts/day_of_preflight.sh`
- Capabilities:
  - API health/state checks
  - optional PocketBase health check
  - optional backend tests / web check / Bedrock smoke
- Smoke-tested successfully against:
  - local API (`127.0.0.1:8010`)
  - PocketBase (`http://18.204.1.6:8090`)
- Updated runbooks:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`

## 2026-03-01 04:52:32 PST

- Added random variant fuzz utility:
  - `scripts/random_variant_fuzz.py`
- Executed sampled fuzz pass:
  - `random_variant_fuzz_6v_seed60001.json`
  - winner counts:
    - EV: `equity_evolved_v1` 5/6
    - first-place: `equity_evolved_v1` 5/6
    - robustness: `equity_evolved_v1` 4/6
- Added summary doc:
  - `research_logs/015_random_variant_fuzz.md`
- Updated day-of guide with optional fuzz command path for weird announcements.

## 2026-03-01 04:44:25 PST

- Updated rolling handoff draft (`research_logs/013_pre7_handoff_draft.md`) to include:
  - preflight command,
  - autosolve guardrail default (`first_gap=0.07`),
  - refreshed run sequence for day-of execution.

## 2026-03-01 04:45:27 PST

- Audited running EC2 instances in `us-east-1` and found multiple active hosts.
- Confirmed workflow target remains PocketBase on `i-0214ea32290cb6b1a` (`18.204.1.6`).
- Added explicit cost-control guidance to `research_logs/004_status_snapshot.md`:
  - list of extra running instance IDs,
  - one command to stop likely idle non-target instances (with verification reminder).

## 2026-03-01 04:46:12 PST

- Re-seeded PocketBase with latest checkpoint commit `8341186`.
- Result:
  - `strategies_updated`: 17
  - champion map remains `equity_evolved_v1` / `meta_switch` / `equity_evolved_v1`.

## 2026-03-01 04:56:54 PST

- Ran expanded random variant fuzz with calibrated budget:
  - `research_logs/experiment_outputs/random_variant_fuzz_16v_seed60111_lowbudget.json`
  - command:
    - `uv run python scripts/random_variant_fuzz.py --n-variants 16 --n-tables 4 --n-games 4 --seed 60111 --out research_logs/experiment_outputs/random_variant_fuzz_16v_seed60111_lowbudget.json`
- Low-budget first-place winners were mixed (`equity_evolved_v1` 11/16 with several outliers), so treated as directional only.

## 2026-03-01 05:03:00 PST

- Re-ran first-place outlier variants with medium-budget multi-seed confirmations:
  - variants: `0, 5, 10, 12, 15`
  - seeds: `61001`, `61002`
  - artifacts: `random_variant_confirm2_first_<idx>_seed<seed>.json`
- Confirmed stable outlier:
  - variant `10` (`start_chips=140`, `ante_amt=50`, `n_orbits=4`, `winner_takes_all`) favored `pot_fraction` in both seeds.
- Sprint split-pot outliers were unstable (alternated between `equity_evolved_v1`, `conservative_plus`, and one `house_hammer`), so no broad split-pot sprint `pot_fraction` rule.
- Added summary doc:
  - `research_logs/016_first_place_fuzz_confirmation.md`

## 2026-03-01 05:08:40 PST

- Updated API dynamic first-place resolver in `game/api.py`:
  - baseline first-place `meta_switch` now requires exact baseline profile, not just profile name.
  - sprint `pot_fraction` override now gated to `winner_takes_all` only.
  - added high-ante-pressure override (`ante_amt/start_chips>=0.33`, `n_orbits>=3`, `winner_takes_all`) -> `pot_fraction`.
- Added/updated regression tests in `tests/test_api_session.py`:
  - split-pot sprint does not force `pot_fraction`.
  - high-ante-pressure rule triggers `pot_fraction`.
  - baseline-name plus overrides resolves as non-baseline first-place.
- Validation:
  - `uv run python -m unittest tests.test_api_session tests.test_llm_advisor`
  - result: `15/15` passing.
- Updated runbooks with new policy:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`
  - `research_logs/006_variant_lookup_table.md`
  - `research_logs/013_pre7_handoff_draft.md`
  - `research_logs/015_random_variant_fuzz.md`

## 2026-03-01 05:12:11 PST

- Aligned `scripts/day_of_autosolve_patch.py` prior selection with updated API first-place resolver logic.
- Changes:
  - exact baseline profile -> first-place prior `meta_switch`.
  - sprint override requires `winner_takes_all`.
  - added high-ante-pressure `winner_takes_all` prior (`ante/start>=0.33`, `n_orbits>=3`) -> `pot_fraction`.
  - fixed script import path bootstrapping for `game.rules` by inserting project root into `sys.path`.
- Dry-run verification (small budget):
  - baseline prior -> `meta_switch`
  - high-ante winner-takes-all prior -> `pot_fraction`
  - sprint split-pot prior -> `equity_evolved_v1`
- Validation:
  - `uv run python -m unittest tests.test_api_session tests.test_llm_advisor` -> `15/15` passing.

## 2026-03-01 05:14:38 PST

- Ran offline policy backtest comparing old vs updated first-place resolver logic on archived variant artifacts.
- Sample criteria:
  - experiment outputs with first-place winner present and strategy set containing `equity_evolved_v1`, `meta_switch`, `pot_fraction`.
  - sample size: `25` artifacts.
- Results:
  - old routing match rate: `10/25` (`0.40`)
  - updated routing match rate: `19/25` (`0.76`)
  - no observed regressions in this sample.
- Added summary doc:
  - `research_logs/017_resolver_policy_backtest.md`

## 2026-03-01 05:18:12 PST

- Improved HUD clarity for day-of rapid decisions:
  - updated `web/src/routes/+page.svelte` to add a `First-place routing cues` block in the session panel.
  - cues now explicitly call out:
    - exact baseline default (`meta_switch`),
    - sprint winner-takes-all `pot_fraction` trigger,
    - high-ante-pressure winner-takes-all `pot_fraction` trigger,
    - sprint split-pot case where sprint trigger is intentionally disabled.
- Web validation:
  - `pnpm -C web check` -> 0 errors / 0 warnings
  - `pnpm -C web build` -> successful production build.
- Updated docs:
  - `research_logs/003_day_of_fast_patch_guide.md`
  - `research_logs/004_status_snapshot.md`
