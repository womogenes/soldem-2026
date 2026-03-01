# Autosolve guardrail calibration

Local time: 2026-03-01 04:10 PST

## Purpose

Validate whether low-budget autosolve (`n_tables=12`, `n_games=8`) plus guardrails reproduces the high-confidence champion map.

## Setup

- Profiles tested:
  - `baseline_v1`
  - `top2_split`
  - sprint override (`baseline_v1` with `{"n_orbits":2,"start_chips":140,"ante_amt":30}`)
- Seeds: `53001`, `53002`, `53003`
- Guardrail defaults:
  - `ev_gap=12.0`
  - `first_gap=0.04` (at calibration time)
  - `robustness_gap=20.0`
- Artifacts:
  - `research_logs/experiment_outputs/autosolve_guardrail_checks/*.json`

## Expected map from higher-budget sweeps

- baseline:
  - EV: `equity_evolved_v1`
  - first-place: `meta_switch`
  - robustness: `equity_evolved_v1`
- top2 split:
  - EV/first-place/robustness: `equity_evolved_v1`
- sprint:
  - EV: `equity_evolved_v1`
  - first-place: `pot_fraction`
  - robustness: `equity_evolved_v1`

## Result

- Accuracy vs expected map across 9 calibration runs:
  - EV:
    - guardrailed: `9/9`
    - raw solver tops: `5/9`
  - first-place:
    - guardrailed: `8/9`
    - raw solver tops: `5/9`
  - robustness:
    - guardrailed: `9/9`
    - raw solver tops: `7/9`

## Interpretation

- Guardrails substantially reduce small-sample noise for EV and robustness.
- First-place remains the noisiest objective at this budget.
- Default was later tightened to `--first-gap 0.07` for safer day-of operation.
