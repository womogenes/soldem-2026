# Pre-7 handoff draft

Local time: 2026-03-01 04:34 PST

## Current recommended champion policy

- EV: `equity_evolved_v1`
- robustness: `equity_evolved_v1`
- first-place:
  - baseline: `meta_switch`
  - non-baseline built-in variants: `equity_evolved_v1`
  - sprint short-stack (`n_orbits<=2` and `start_chips<=150`): `pot_fraction`
  - passive high-confidence table read: `pot_fraction`

## Fast day-of commands

0. Optional preflight:
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --pb-url http://18.204.1.6:8090`

1. Apply profile quickly:
- `uv run python scripts/day_of_patch.py --preset baseline`

2. One-command autosolve and patch:
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '{"n_orbits":2,"start_chips":140,"ante_amt":30}' --n-tables 12 --n-games 8 --seed 42`

3. Keep dynamic resolution after autosolve:
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --keep-dynamic`

## Runtime checks

- Autosolve default runtime benchmark: about `22.9s`.
- Autosolve first-place guardrail default: `first_gap=0.07`.
- Backend tests currently passing: `19/19`.
- Frontend check/build passing.

## Latest key docs

- `research_logs/004_status_snapshot.md`
- `research_logs/006_variant_lookup_table.md`
- `research_logs/008_weird_variant_stress.md`
- `research_logs/009_autosolve_guardrail_calibration.md`
- `research_logs/011_horizon_sensitivity.md`
- `research_logs/012_first_place_horizon_check.md`
