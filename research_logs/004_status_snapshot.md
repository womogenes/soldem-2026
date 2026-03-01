# Status snapshot and operator guide

Local time: 2026-03-01 02:00 PST

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
6. PocketBase EC2 deployment + schema sync + metadata seeding.

## Best strategy recommendations from rollouts

Primary recommendation for day-of EV stability:
- `conservative_plus`

First-place/correlation-heavy fallback:
- `equity_evolved_v1`

High-variance exploit mode (only if table looks soft/passive):
- `pot_fraction`

Observed horizon tendencies from `iter2_small` matrix:
- 5-game windows: `conservative_plus` slightly favored.
- 10-game windows: evolved/sniper family leads most often.
- 20-game windows: `conservative_plus` regains edge.

Observed field-type tendencies from `hero_suite_v2`:
- mixed pool: `equity_sniper_ultra` 6/9 scenario wins.
- shark pool: `equity_sniper_ultra` 9/9 scenario wins.
- chaos pool: `conservative_plus` 9/9 scenario wins.
- practical takeaway: when table looks disciplined/tight, prefer sniper mode; when table is erratic, stay conservative.

Adaptive strategy experiment:
- `meta_switch` was tested but did not beat fixed champions on EV robustness.
- keep it as optional high-variance fallback only.

## How to run now

1. Start backend API.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Start HUD web app.
`pnpm -C web dev --host`

3. Open HUD and use quick controls.
- Set objective (`ev` recommended by default).
- Click `Use objective champion`.
- Enter state and click `Get recommendation`.
- As events accumulate, use `Use auto table read preset` to apply mode-aware switching.
- Auto table-read mode map:
  - `competitive` or `correlated_pair`: prefer evolved attack (`equity_evolved_v1`).
  - `aggressive` / chaotic: prefer conservative (`conservative_plus`).
  - `passive` + first-place objective: may move to `pot_fraction`.

## Day-of fast patch

Use one command to apply profile variants:
`uv run python scripts/day_of_patch.py --preset high_low_split`

For custom host-announced changes:
`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4,"ante_amt":30}'`

For manual champion locks:
`uv run python scripts/day_of_patch.py --preset baseline --set-ev conservative_plus --set-first-place equity_evolved_v1 --set-robustness conservative_plus`

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
