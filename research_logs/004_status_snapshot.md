# Status snapshot and operator guide

Local time: 2026-03-01 03:44 PST

## Reference

This workstream follows `research_logs/000_god_prompt.md` as the controlling spec for continuation and compaction.

## What is implemented

1. Strategy search and rollout framework with compact JSONL/matrix logging.
2. Expanded strategy pool with new contenders:
- `conservative_plus`
- `equity_evolved_v1`
- `equity_sniper_ultra`
- `equity_sniper_plus`
- `equity_flex`
- `equity_balanced`
- `equity_harvest`
- `house_hammer`
3. Hero-vs-opponent-pool benchmark harness (`scripts/benchmark_hero.py`).
4. Rule-profile-aware API champion resolution and HUD quick preset controls.
5. Day-of fast patch script and guide.
6. One-command autosolve+patch helper:
- `scripts/day_of_autosolve_patch.py`
- includes prior-guardrail filtering to reduce low-sample solver noise by default.
7. PocketBase EC2 deployment + schema sync + metadata seeding.

## Best strategy recommendations from rollouts

Primary recommendation for day-of EV stability:
- `equity_evolved_v1`

First-place/correlation-heavy fallback:
- baseline rules: `meta_switch`
- non-baseline built-in variants: `equity_evolved_v1`

High-variance exploit mode (only if table looks soft/passive):
- `pot_fraction`

Latest evidence:
- six-profile short-horizon sweep (`n_tables=50`, `n_games=10`):
  - EV winner: `equity_evolved_v1` in 6/6 profiles
  - robustness winner: `equity_evolved_v1` in 6/6 profiles
  - first-place winner: `equity_evolved_v1` in 4/6, `meta_switch` in 2/6
- baseline first-place tie-break (`n_tables=150`): `meta_switch` edge over `equity_evolved_v1`.
- seller-self-bid first-place tie-break (`n_tables=150`): `equity_evolved_v1` edge over `meta_switch`.
- weird-variant stress runs (`n_tables=40`) show:
  - EV and robustness: `equity_evolved_v1` in 5/5 tested mixed overrides.
  - first-place: `pot_fraction` only in sprint profiles (`n_orbits=2`, low starting stacks).
- horizon sensitivity check (`5/10/20` games, none+respect correlation):
  - EV winner remained `equity_evolved_v1` in all tested horizons and regimes.

## How to run now

1. Start backend API.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Start HUD web app.
`pnpm -C web dev --host`

3. Open HUD and use quick controls.
- Set objective (`ev` recommended by default).
- Click `Use objective champion`.
- Enter state and click `Get recommendation`.
- Optional second opinion: click `Get LLM hint` (Bedrock-backed, deterministic recommendation remains primary).
- Recommendation and LLM panels now show resolved strategy reason labels (for example `baseline_balanced_first_place`, `sprint_profile_first_place`).
- As events accumulate, use `Use auto table read preset` to apply mode-aware switching.
- Auto table-read mode map:
  - EV/robustness: keep `equity_evolved_v1`.
  - first-place + baseline:
    - balanced/calm: `meta_switch`
    - competitive/correlated/aggressive: `equity_evolved_v1`
  - `passive` + first-place objective: may move to `pot_fraction`.

## Day-of fast patch

Use one command to apply profile variants:
`uv run python scripts/day_of_patch.py --preset high_low_split`

For custom host-announced changes:
`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4,"ante_amt":30}'`

For manual champion locks:
`uv run python scripts/day_of_patch.py --preset baseline --set-ev equity_evolved_v1 --set-first-place meta_switch --set-robustness equity_evolved_v1`

For quick empirical champion probe under a new variant:
`uv run python scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"n_orbits":4}' --n-tables 12 --n-games 8 --out research_logs/experiment_outputs/live_variant_probe.json`

Current lookup reference:
- `research_logs/006_variant_lookup_table.md`

See `research_logs/003_day_of_fast_patch_guide.md` for full decision flow.

## PocketBase status

Deployed endpoint:
- `http://18.204.1.6:8090`

Provisioning and sync commands:
- `bash scripts/aws/provision_pocketbase_ec2.sh ...`
- `uv run python scripts/sync_pocketbase_schema.py ...`
- `uv run python scripts/seed_pocketbase.py ...`

Current seeded collections:
- `strategies`: 17
- `champions`: 3
- `eval_runs`: 4

## Cost and safety notes

1. Restrict inbound security group CIDRs before event time.
2. Rotate PocketBase admin credentials after session.
3. Stop EC2 instance when idle to reduce spend:
`aws ec2 stop-instances --region us-east-1 --instance-ids i-0214ea32290cb6b1a`
