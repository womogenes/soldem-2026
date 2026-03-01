# First-place horizon check

Local time: 2026-03-01 04:29 PST

## Goal

Evaluate first-place objective strategy across short and long horizons for baseline rules, including correlated human-like dynamics.

## Setup

- Script: `scripts/benchmark_hero.py`
- Heroes: `equity_evolved_v1`, `meta_switch`, `pot_fraction`, `conservative_plus`
- Objective: `first_place`
- Rule profile: `baseline_v1`
- Horizons: `5`, `10`, `20` games
- Regimes:
  - none correlation (`mode=none`)
  - respect correlation (`mode=respect`, strength `0.35`, pair `1-2`)
- Budget: `n_tables=80`
- Extra seeds run for ambiguous respect cases:
  - 5-game: seeds `56105`, `56106`, `56107`
  - 10-game: seeds `56110`, `56111`, `56112`
  - 20-game: seeds `56120`, `56121`, `56122`

## Key findings

1. none correlation
- `equity_evolved_v1` and `meta_switch` are close on first-place rate.
- `equity_evolved_v1` is far better on EV and downside tail, but objective here is first-place only.

2. respect correlation (0.35), multi-seed aggregate
- 5-game mean first-place:
  - `meta_switch`: `0.410`
  - `equity_evolved_v1`: `0.348`
- 10-game mean first-place:
  - `meta_switch`: `0.401`
  - `equity_evolved_v1`: `0.370`
- 20-game mean first-place:
  - `meta_switch`: `0.376`
  - `equity_evolved_v1`: `0.349`

3. `pot_fraction`
- strong only in sprint-profile rules; under baseline it underperformed first-place in this check.

## Decision impact

- Keep baseline first-place default on `meta_switch`.
- Keep sprint or passive-high-confidence overrides to `pot_fraction`.
- Keep EV/robustness defaults on `equity_evolved_v1`.

## Artifacts

- none:
  - `research_logs/experiment_outputs/night_horizon_first_5g_none_seed56005.json`
  - `research_logs/experiment_outputs/night_horizon_first_10g_none_seed56010.json`
  - `research_logs/experiment_outputs/night_horizon_first_20g_none_seed56020.json`
- respect 0.35:
  - `research_logs/experiment_outputs/night_horizon_first_5g_respect35_seed56105.json`
  - `research_logs/experiment_outputs/night_horizon_first_5g_respect35_seed56106.json`
  - `research_logs/experiment_outputs/night_horizon_first_5g_respect35_seed56107.json`
  - `research_logs/experiment_outputs/night_horizon_first_10g_respect35_seed56110.json`
  - `research_logs/experiment_outputs/night_horizon_first_10g_respect35_seed56111.json`
  - `research_logs/experiment_outputs/night_horizon_first_10g_respect35_seed56112.json`
  - `research_logs/experiment_outputs/night_horizon_first_20g_respect35_seed56120.json`
  - `research_logs/experiment_outputs/night_horizon_first_20g_respect35_seed56121.json`
  - `research_logs/experiment_outputs/night_horizon_first_20g_respect35_seed56122.json`
