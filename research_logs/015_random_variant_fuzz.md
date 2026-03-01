# Random variant fuzz check

Local time: 2026-03-01 04:50 PST

## Goal

Probe surprise rule mixes beyond named presets using random override sampling.

## Method

- Script: `scripts/random_variant_fuzz.py`
- Run:
  - `--n-variants 6 --n-tables 10 --n-games 8 --seed 60001`
- Artifact:
  - `research_logs/experiment_outputs/random_variant_fuzz_6v_seed60001.json`

## Winner counts

- EV winners:
  - `equity_evolved_v1`: 5/6
  - `equity_sniper_ultra`: 1/6
- first-place winners:
  - `equity_evolved_v1`: 5/6
  - `conservative_plus`: 1/6
- robustness winners:
  - `equity_evolved_v1`: 4/6
  - `equity_sniper_ultra`: 1/6
  - `meta_switch`: 1/6

## Interpretation

- Random override fuzz supports keeping `equity_evolved_v1` as default EV/robustness anchor.
- No broad evidence from this pass to replace baseline first-place default `meta_switch`.
- Keep using sprint/passive `pot_fraction` overrides when those specific conditions are met.

## Follow-up

- A larger low-budget random sweep and seeded first-place outlier confirmations were run later.
- See `research_logs/016_first_place_fuzz_confirmation.md` for the updated policy:
  - sprint override narrowed to winner-takes-all profiles,
  - added high-ante-pressure winner-takes-all `pot_fraction` trigger.

## Command

```bash
uv run python scripts/random_variant_fuzz.py --n-variants 6 --n-tables 10 --n-games 8 --seed 60001 --out research_logs/experiment_outputs/random_variant_fuzz_6v_seed60001.json
```
