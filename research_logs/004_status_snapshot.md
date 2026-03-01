# Status snapshot and operator guide

Local time: 2026-03-01 02:00 PST

## Reference

This workstream follows `research_logs/000_god_prompt.md` as the controlling spec for continuation and compaction.

## What is implemented

1. Strategy search and rollout framework with compact JSONL/matrix logging.
2. Expanded strategy pool with new contenders:
- `conservative_plus`
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
- `equity_sniper_ultra`

High-variance exploit mode (only if table looks soft/passive):
- `pot_fraction`

Observed horizon tendencies from `iter2_small` matrix:
- 5-game windows: `conservative_plus` slightly favored.
- 10-game windows: `equity_sniper_ultra` leads most often.
- 20-game windows: `conservative_plus` regains edge.

## How to run now

1. Start backend API.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Start HUD web app.
`pnpm -C web dev --host`

3. Open HUD and use quick controls.
- Set objective (`ev` recommended by default).
- Click `Use objective champion`.
- Enter state and click `Get recommendation`.

## Day-of fast patch

Use one command to apply profile variants:
`uv run python scripts/day_of_patch.py --preset high_low_split`

For custom host-announced changes:
`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4,"ante_amt":30}'`

See `research_logs/003_day_of_fast_patch_guide.md` for full decision flow.

## PocketBase status

Deployed endpoint:
- `http://18.204.1.6:8090`

Provisioning and sync commands:
- `bash scripts/aws/provision_pocketbase_ec2.sh ...`
- `uv run python scripts/sync_pocketbase_schema.py ...`
- `uv run python scripts/seed_pocketbase.py ...`

Current seeded collections:
- `strategies`: 15
- `champions`: 3
- `eval_runs`: 4

## Cost and safety notes

1. Restrict inbound security group CIDRs before event time.
2. Rotate PocketBase admin credentials after session.
3. Stop EC2 instance when idle to reduce spend:
`aws ec2 stop-instances --region us-east-1 --instance-ids i-0214ea32290cb6b1a`
