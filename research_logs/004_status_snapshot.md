# Status snapshot and operator guide

Local time: 2026-03-01 06:34 PST

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
5. Simulation and quick-solver path now supports variable player counts (`n_players != 5`) for day-of variant probing.
6. Day-of fast patch script and guide.
7. One-command autosolve+patch helper:
- `scripts/day_of_autosolve_patch.py`
- includes prior-guardrail filtering to reduce low-sample solver noise by default.
- prior map is aligned with live resolver first-place rules (exact baseline, winner-takes-all banding, passive-table override).
8. PocketBase EC2 deployment + schema sync + metadata seeding.

## Best strategy recommendations from rollouts

Primary recommendation for day-of EV stability:
- `equity_evolved_v1`

First-place/correlation-heavy fallback:
- exact baseline rules: `meta_switch`
- winner-takes-all sprint profile (`n_orbits<=2`, `start_chips<=150`): `pot_fraction`
- winner-takes-all pot-pressure band (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)): `pot_fraction`
- winner-takes-all high-stack low-ante band (`n_orbits>=3`, `start_chips>=180`, `ante/start<0.20`): `equity_evolved_v1`
- remaining non-sprint winner-takes-all band: `meta_switch`
- non-winner-takes-all variants: `equity_evolved_v1`

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
- random-variant fuzz recheck + seeded confirmations:
  - sprint override should be constrained to `winner_takes_all` (split-pot sprint outliers did not consistently favor `pot_fraction`).
  - high ante pressure winner-takes-all (`140/50`, `n_orbits=4`) repeatedly favored `pot_fraction`.
- winner-takes-all banding recalibration + boundary confirms:
  - artifacts now include 8/10/12-game horizon matrices and hero-vs-pool boundary probes at `start=140/150/160/180/200`.
  - strongest offline policy fit on current artifact set: first-place WTA banding around `ante/start>=0.25` plus high-stack low-ante relief.
  - summary: `research_logs/018_ante_threshold_calibration.md`
- resolver policy backtest over archived variant artifacts:
  - old first-place routing match rate: `10/25` (`0.40`)
  - updated routing match rate: `19/25` (`0.76`)
  - summary: `research_logs/017_resolver_policy_backtest.md`
- horizon sensitivity check (`5/10/20` games, none+respect correlation):
  - EV winner remained `equity_evolved_v1` in all tested horizons and regimes.
- first-place horizon check (`5/10/20`, respect 0.35 with multi-seed):
  - baseline first-place mean favored `meta_switch`, so baseline first-place default stays `meta_switch`.

## How to run now

1. Start backend API.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Start HUD web app.
`pnpm -C web dev --host`

3. Optional quick preflight.
`bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --pb-url http://18.204.1.6:8090`
Policy-routing smoke option:
`bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke`
Latest integrated preflight (`tests + web + policy smoke`) completed at `2026-03-01 06:42 PST` using API `:8018`.
Latest full-stack preflight including PocketBase + Bedrock completed at `2026-03-01 05:52 PST` using API `:8015`.
Latest policy-smoke pass completed at `2026-03-01 06:42 PST` using API `:8018` with expanded WTA branch checks.
Full backend discovery tests currently pass: `32/32`.
Bedrock smoke check is included in the full-stack preflight above.

4. Open HUD and use quick controls.
- Set objective (`ev` recommended by default).
- Click `Use objective champion`.
- Enter state and click `Get recommendation`.
- Optional second opinion: click `Get LLM hint` (Bedrock-backed, deterministic recommendation remains primary).
- Recommendation and LLM panels now show resolved strategy reason labels and backend-authored plain-English reason text.
- HUD now renders plain-English descriptions for strategy reason codes in recommendation and LLM hint panels.
- HUD now shows a dedicated `First-place routing cues` block in the session panel to make baseline/sprint/WTA-band triggers visible without parsing raw JSON.
- API exports these cues as `first_place_policy_cues` in `/session/state` for deterministic client or script checks.
- As events accumulate, use `Use auto table read preset` to apply mode-aware switching.
- Auto table-read mode map:
  - EV/robustness: keep `equity_evolved_v1`.
  - first-place + exact baseline: `meta_switch`
  - first-place + non-sprint winner-takes-all: follow WTA banding cues (`pot_fraction` / `meta_switch` / `equity_evolved_v1`)
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
3. Multiple EC2 instances are currently running in `us-east-1`; active PocketBase target in this workflow is:
- `i-0214ea32290cb6b1a` (`18.204.1.6`)
4. Stop idle non-target instances to reduce spend (verify before running):
`aws ec2 stop-instances --region us-east-1 --instance-ids i-0952920bc2c2dd3f7 i-03d70cfd94261af31 i-0854d429f873e6c52 i-08f41ea7a4d11aaca i-0a229522e15035179`
