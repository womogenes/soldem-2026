# Day-of runbook

Local timestamp: 2026-03-01 01:20 PST

## Startup sequence

1. Start backend API:
```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

2. Start HUD:
```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

3. Open HUD at `http://127.0.0.1:5173`.

4. Optional: recompute champions (quick refresh):
```bash
curl -s -X POST http://127.0.0.1:8000/strategies/recompute_champions \
  -H 'content-type: application/json' \
  -d '{"n_matches":60,"n_games_per_match":10,"seed":42}'
```

## Live operation loop

1. Enter current phase and state in HUD.
2. Enter your cards, auction cards, and updated stacks.
3. Keep output mode on `all` when uncertain, otherwise switch to preferred mode.
4. Log observed events using session tracking panel:
- bids
- auction results
- showdown notes

5. Execute recommended action with human override if table dynamics require it.

## Objective and mode controls

- Objective options:
  - `ev`
  - `first_place`
  - `robustness`
- Output modes:
  - `action_first`
  - `top3`
  - `metrics`
  - `all`

## Fast troubleshooting

### Backend not responding
```bash
curl -s http://127.0.0.1:8000/health
```

### Session state sanity check
```bash
curl -s http://127.0.0.1:8000/session/state | jq '{rule_profile, champions, events_count}'
```

### Reset session profiles/events
```bash
curl -s -X POST http://127.0.0.1:8000/session/reset
```

### Apply emergency rule patch
Use [day_of_patch_guide.md](/home/willi/coding/trading/soldem-2026/v2/docs/day_of_patch_guide.md).

## AWS optional workflow

- Provision PocketBase:
```bash
scripts/aws/provision_pocketbase_ec2.sh --key-name <ec2-key-name> --name soldem-pocketbase
```
- Launch worker swarm:
```bash
scripts/aws/launch_worker_swarm.sh --key-name <ec2-key-name> --repo <git-url> --pocketbase-url http://<ip>:8090 --count 4
```
