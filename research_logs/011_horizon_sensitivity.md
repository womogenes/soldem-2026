# Horizon sensitivity check

Local time: 2026-03-01 04:22 PST

## Goal

Re-check strategy strength for fewer vs more games with the latest strategy set, since day-of sessions may be short (`~10` games).

## Setup

- Script: `scripts/benchmark_hero.py`
- Heroes: `equity_evolved_v1`, `meta_switch`, `conservative_plus`, `equity_sniper_ultra`
- Opponent pool: mixed
- Objective: `ev`
- Horizons tested: `5`, `10`, `20` games
- Two table regimes:
  - no correlation (`mode=none`)
  - respect correlation (`mode=respect`, strength `0.35`, pair `1-2`)
- Budget per point: `n_tables=80`

## Results summary

1. no correlation
- 5 games: `equity_evolved_v1` first by mean EV and first-place rate.
- 10 games: `equity_evolved_v1` first by clear margin.
- 20 games: `equity_evolved_v1` first by clear margin.

2. respect correlation (0.35)
- 5 games: `equity_evolved_v1` first by clear margin.
- 10 games: `equity_evolved_v1` first by clear margin.
- 20 games: `equity_evolved_v1` first by clear margin.

## Implication

- No horizon in this sweep favored switching EV default away from `equity_evolved_v1`.
- Prior guidance that `conservative_plus` regains edge on longer windows is not supported by the latest evolved strategy runs.
- Keep EV/robustness defaults on `equity_evolved_v1` for 5/10/20-game planning.

## Artifacts

- no correlation:
  - `research_logs/experiment_outputs/night_horizon_ev_5g_none_seed55005.json`
  - `research_logs/experiment_outputs/night_horizon_ev_10g_none_seed55010.json`
  - `research_logs/experiment_outputs/night_horizon_ev_20g_none_seed55020.json`
- respect 0.35:
  - `research_logs/experiment_outputs/night_horizon_ev_5g_respect35_seed55105.json`
  - `research_logs/experiment_outputs/night_horizon_ev_10g_respect35_seed55110.json`
  - `research_logs/experiment_outputs/night_horizon_ev_20g_respect35_seed55120.json`
