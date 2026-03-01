# Correlation strength first-place check

Local time: 2026-03-01 04:16 PST

## Goal

Check whether baseline first-place should always use `meta_switch`, or if correlated/competitive environments favor `equity_evolved_v1`.

## Setup

- Script: `scripts/benchmark_hero.py`
- Heroes: `meta_switch`, `equity_evolved_v1`, `pot_fraction`
- Opponent pool: mixed human-like set
- Objective: `first_place`
- Rule profile: `baseline_v1`
- Correlation mode: `respect` (pair `1-2`)
- Strength sweep: `0.0`, `0.2`, `0.35`, `0.5`, `0.7`
- Budget each point: `n_tables=100`, `n_games=10`

## Results

1. strength `0.00`
- `equity_evolved_v1` first-place `0.378`
- `meta_switch` first-place `0.369`

2. strength `0.20`
- `meta_switch` first-place `0.367`
- `equity_evolved_v1` first-place `0.338`

3. strength `0.35`
- `equity_evolved_v1` first-place `0.388`
- `meta_switch` first-place `0.336`

4. strength `0.50`
- `meta_switch` first-place `0.423`
- `equity_evolved_v1` first-place `0.419`

5. strength `0.70`
- `equity_evolved_v1` first-place `0.359`
- `meta_switch` first-place `0.348`

`pot_fraction` underperformed first-place on baseline in this sweep.

## Takeaway

- This sweep showed mixed outcomes and was treated as exploratory.
- A later multi-seed horizon check (`research_logs/011_horizon_sensitivity.md` plus added first-place seed extensions) favored `meta_switch` for baseline first-place on average.
- Final policy kept in API:
  - baseline first-place: `meta_switch`
  - passive high-confidence or sprint short-stack: `pot_fraction`

## Artifacts

- `research_logs/experiment_outputs/night_corr_strength_0p00_seed54000.json`
- `research_logs/experiment_outputs/night_corr_strength_0p20_seed54020.json`
- `research_logs/experiment_outputs/night_corr_strength_0p35_seed54035.json`
- `research_logs/experiment_outputs/night_corr_strength_0p50_seed54050.json`
- `research_logs/experiment_outputs/night_corr_strength_0p70_seed54070.json`
