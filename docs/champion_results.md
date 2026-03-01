# Champion results summary

Local timestamp: 2026-03-01 06:44:00 PST

## Final validation outcome

After extended multi-stage search and long revalidation:

- EV-safe champion: `market_maker_v2` (`reserve_frac=0.09`)
- Robustness-safe champion: `regime_switch_v2`
- Tournament-win champion: `market_maker_v2`
- High-variance first-place override: `pot_fraction` (not EV-safe)

## Finalist long validation

From:

- `research_logs/experiment_outputs/finalists_long_ev.json`
- `research_logs/experiment_outputs/finalists_long_first_place.json`
- `research_logs/experiment_outputs/finalists_long_robustness.json`

Setup:

- 3 seeds (`6101,6102,6103`)
- 380 matches per seed per cell
- horizons `5,10,20`
- correlation modes `none,respect,herd,kingmaker`
- finalist pool included `mm_r0090` (`market_maker_v2`), `mm_r0095` (`market_maker_tight`), `rs_v2` (`regime_switch_v2`), `regime_switch_robust`, and baseline opponents

Results:

- EV objective winner: `mm_r0090` in all cells (`12/12`).
- Robustness objective winner: `rs_v2` in all cells (`12/12`).
- First-place-rate objective winner: `pot_fraction` in all cells (`12/12`) but with large negative EV.

Aggregate EV across all finalist-long runs:

- `mm_r0090`: `26.047`
- `market_maker_tight`: `20.544`
- `rs_v2`: `16.593`
- `regime_switch_robust`: `15.817`

## Tournament-win validation

From:

- `research_logs/experiment_outputs/finalists_tournament_win_fast.json`
- `research_logs/experiment_outputs/finalists_long_tournament_win.json`

Setup:

- objective: `tournament_win`
- fast pass: 3 seeds (`9811,9822,9833`), 250 matches per seed/cell
- long pass: 4 seeds (`9911,9922,9933,9944`), 500 matches per seed/cell
- horizon `10`
- correlation modes `none,respect,herd,kingmaker`
- finalist pool: `market_maker_v2`, `market_maker_tight`, `regime_switch_v2`, `regime_switch_robust`, `market_maker`, `regime_switch`, `conservative_ultra`, `pot_fraction`, `random`, `bully`

Result:

- `market_maker_v2` wins all tournament-win correlation cells (`4/4`) in both fast and long passes.
- Mean `tournament_win_rate` across long-pass cells:
- `market_maker_v2`: `0.355`
- `market_maker_tight`: `0.288`
- `regime_switch_v2`: `0.256`

Direct EV disambiguation artifact:

- `research_logs/experiment_outputs/mmv2_vs_tight_h2h.json`

## Rule-profile validation

From `research_logs/experiment_outputs/rule_profile_validation_long.json`:

- 6 profiles x 3 objectives x 3 seeds, 320 matches per seed/cell.
- Objective-metric winners can be high variance for `first_place` (often `pot_fraction` / `random`).
- EV-constrained defaults remain stable and are mapped in `game/api.py` through `PROFILE_OBJECTIVE_DEFAULTS`.

## Correlation stress test

From `research_logs/experiment_outputs/correlation_stress_matrix.json` (81 scenarios with stronger correlation and adversarial pairs):

- EV winners by frequency:
  - `market_maker_tight`: `50/81`
  - `regime_switch_robust`: `23/81`
  - others: `8/81`

Interpretation:

- Correlation shocks favor tighter reserve styles; the `v2` champion set remains in this same family and is selected from stronger finalist-long head-to-head comparisons.

## Operational recommendation

- Default objective strategy: `market_maker_v2`
- Robust fallback strategy: `regime_switch_v2`
- Optional high-variance upside mode: `pot_fraction` (use only when accepting EV downside)
