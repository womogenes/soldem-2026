# Champion results summary

Local timestamp: 2026-03-01 03:10:00 PST

## Long validation matrix (high confidence)

From:

- `research_logs/experiment_outputs/long_validation_ev.json`
- `research_logs/experiment_outputs/long_validation_first_place.json`
- `research_logs/experiment_outputs/long_validation_robustness.json`

Setup:

- 3 seeds (`5001,5002,5003`)
- 450 matches per seed per cell
- horizons `5,10,20`
- correlation modes `none,respect,herd,kingmaker`
- strategy pool included `market_maker_tight`, `regime_switch_robust`, `market_maker`, `regime_switch`, `market_maker_aggr`, `conservative_ultra`, `conservative`, `elastic_conservative`, `pot_fraction`, `random`, `bully`

Results (objective-metric winners):

- `market_maker_tight` won all EV cells (`12/12`).
- `pot_fraction` won first-place-rate cells (`12/12`) but with negative EV in most baseline-like settings.
- `regime_switch_robust` won all robustness cells (`12/12`).
- Overall EV mean across all 108 long runs:
  - `market_maker_tight`: `34.814`
  - `regime_switch_robust`: `31.132`
  - `market_maker`: `21.792`

## Rule-profile validation (high confidence)

From `research_logs/experiment_outputs/rule_profile_validation_long.json`:

- 6 rule profiles x 3 objectives x 3 seeds
- 320 matches per seed per profile/objective cell

Profile/objective winners (objective-metric winners):

- `market_maker_tight` won all EV cells (`6/6`).
- `first_place` winner is profile-dependent and often high-variance (`pot_fraction`, occasionally `random`) outside split-pot variants.
- `regime_switch_robust` won all robustness cells (`6/6`).

Exported lookup:

- `research_logs/champion_lookup_from_rule_profile_validation_long.json`

## Extreme correlation stress test

From `research_logs/experiment_outputs/correlation_stress_matrix.json`:

- 81 additional scenarios over stronger correlation strengths (`0.35`, `0.5`, `0.7`) and adversarial pair structures.
- EV winners:
  - `market_maker_tight`: `50/81`
  - `regime_switch_robust`: `23/81`
  - others: `8/81`
- Objective-metric winners include high-variance `pot_fraction`/`random` in first-place mode; these remain optional overrides, not safe defaults.

## Operational recommendation

- Default objective strategy: `market_maker_tight`
- Robust fallback strategy: `regime_switch_robust`
- High-variance override for pure win-rate chasing: `pot_fraction` (use only when accepting EV downside).
