# Day-of patch guide

Local timestamp: 2026-03-01 01:19 PST

This guide is for applying unknown rule changes in under 2 minutes.

## Two-minute patch flow

1. Start backend if needed:
```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```
2. Apply a profile or overrides instantly:
```bash
python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```
3. Validate active rule profile:
```bash
curl -s http://127.0.0.1:8000/session/state | jq '.rule_profile'
```
4. Refresh HUD and continue play.

## Common patch recipes

### Seller can bid own auction
```bash
python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

### No multi-card auction
```bash
python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"allow_multi_card_sell": false}'
```

### Ranking changes to standard poker-style
```bash
python scripts/apply_rule_patch.py --profile standard_rankings
```

### Pot split top two hands
```bash
python scripts/apply_rule_patch.py --profile top2_split
```

### High-low split
```bash
python scripts/apply_rule_patch.py --profile high_low_split
```

### Different ante or orbit count
```bash
python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"ante_amt": 30, "n_orbits": 4}'
```

## Weird variation handling

If a variation is not represented by built-in flags, do this:

1. Apply closest override now so HUD stays operational.
2. Record exact variation in session notes:
```bash
curl -s -X POST http://127.0.0.1:8000/session/event \
  -H 'content-type: application/json' \
  -d '{"event_type":"note","note":"Day-of rule: ..."}'
```
3. Update `game/rules.py` with a new profile after the round and hot-reload backend.

## Precomputed variant leaderboard refresh

Run this in background before gameplay if time allows:
```bash
python scripts/precompute_variants.py
```
