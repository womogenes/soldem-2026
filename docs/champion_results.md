# Champion results summary

Local timestamp: 2026-03-01 01:45:00 PST

## Baseline candidate sweep

From `research_logs/experiment_outputs/candidates_*.json`:

- `market_maker` won EV in all 12 objective/correlation runs.
- Mean EV across those runs:
  - `market_maker`: `113.445`
  - `conservative_ultra`: `86.253`
  - `conservative`: `68.203`

## Horizon and correlation matrix

From `research_logs/experiment_outputs/horizon_correlation_matrix.json`:

- Across 27 runs (3 objectives x 3 horizons x 3 correlation modes):
  - `market_maker` won 25 runs.
  - `conservative_ultra` won 2 runs (robustness + high-correlation settings).

## Rule-variant matrix

From `research_logs/experiment_outputs/rule_variant_matrix.json`:

- `market_maker` won 14 of 18 profile/objective cells.
- `conservative_ultra` won 3 robustness-focused cells.
- `conservative` won 1 standard-ranking first-place cell.

## Operational recommendation

- Default strategy: `market_maker`.
- Robust fallback: `conservative_ultra`.
- If ranking policy is explicitly `standard_plus_five_kind` and objective is first-place, consider `conservative`.
