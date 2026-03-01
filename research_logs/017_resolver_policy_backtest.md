# Resolver policy backtest

Local time: 2026-03-01 05:14 PST

## Goal

Estimate whether the updated first-place resolver rules better match historical variant-winner evidence than the previous rule logic.

## Method

- Compared old vs updated first-place routing logic on archived `research_logs/experiment_outputs/*.json` artifacts that include:
  - `objective_winners.first_place.winner`
  - strategy set containing `equity_evolved_v1`, `meta_switch`, and `pot_fraction`.
- Sample size: `25` artifact rows.
- Old logic:
  - sprint short-stack (`n_orbits<=2`, `start_chips<=150`) => `pot_fraction`
  - else baseline name => `meta_switch`
  - else => `equity_evolved_v1`
- Updated logic:
  - sprint short-stack with `winner_takes_all` => `pot_fraction`
  - high-ante-pressure winner-takes-all (`ante/start>=0.33`, `n_orbits>=3`) => `pot_fraction`
  - exact baseline profile => `meta_switch`
  - otherwise => `equity_evolved_v1`

## Result

- Old logic match rate: `10/25 = 0.40`
- Updated logic match rate: `19/25 = 0.76`
- Net: `+9` additional matches, no observed regressions in this sample.

## Interpretation

- This is an offline artifact backtest, not a strict unbiased holdout.
- Still, the direction is strong enough to justify keeping the updated resolver and autosolve prior rules for day-of use.
- This report predates the later winner-takes-all banding recalibration. See `research_logs/018_ante_threshold_calibration.md`.
