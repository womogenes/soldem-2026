# Day-of rapid patch guide for rule variations

Local timestamp: 2026-03-01 01:40:32 PST

## Goal

Apply new Sold 'Em rule variations and refresh recommendations in under 2 minutes.

## Assumed baseline

- Source of truth remains `RULES.md`.
- Runtime service: `game/api.py` (FastAPI).
- Rule model: `game/rules.py` (`RuleProfile` + `resolve_profile`).
- Engine behavior: `game/engine_base.py`.
- Strategy selection API: `/strategies/recompute_champions`.
- Artifact champion load API: `/strategies/load_champions`.

## Two-minute patch flow

### Step 1: apply known-field variations without code edits (15-30s)

Use API overrides when variation only changes existing fields:

- `n_orbits`
- `allow_multi_card_sell`
- `seller_can_bid_own_card`
- `hand_ranking_policy`
- `pot_distribution_policy`
- `start_chips`
- `ante_amt`

Command:

```bash
curl -sS -X POST http://127.0.0.1:8000/rules/apply_profile \
  -H 'content-type: application/json' \
  -d '{
    "profile_name": "baseline_v1",
    "overrides": {
      "n_orbits": 4,
      "seller_can_bid_own_card": true
    }
  }'
```

### Step 2: recompute champions quickly (45-90s)

Command:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/recompute_champions \
  -H 'content-type: application/json' \
  -d '{"n_matches": 35, "n_games_per_match": 8, "seed": 20260301}'
```

If latency budget is tighter, use:

- `n_matches=20`
- `n_games_per_match=6`

### Step 3: verify HUD state (10-20s)

Command:

```bash
curl -sS http://127.0.0.1:8000/session/state | jq '.rule_profile,.champions'
```

## Precomputed fallback mapping

Current objective-specific fallback set:

- `ev`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
- `first_place`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`
- `robustness`: `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`

If recompute fails on day-of, load latest artifact champion map:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path": null}'
```

Higher-confidence distributed fallback maps are also available:

- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-015615.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-020134.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-021037.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-023132.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_precomputed_variation_champions_20260301-031824.json`
- `research_logs/experiment_outputs/distributed_master_summary_20260301.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-030400.json`
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-033100.json`

## Patch templates for unknown new rule types

### New showdown payout mode

1. Add new literal in `game/rules.py` `PotDistributionPolicy`.
2. Add branch in `game/engine_base.py` `_resolve_showdown`.
3. Add a built-in profile in `built_in_profiles()`.
4. Re-run tests:

```bash
uv run python -m unittest discover -s tests -v
```

### New ranking order

1. Add policy literal in `game/rules.py`.
2. Add ordering/table logic in `game/utils.py`:
- `ranking_order`
- `_category_rank_map`
3. Add tests in `tests/test_hand_ranking.py`.

### Community cards introduced

1. Add `community_cards` state in `Game`.
2. During showdown, evaluate `player_cards[i] + community_cards`.
3. Update API request schema (`RecommendationReq`) and HUD input fields.

### Auction timing or tie-break change

1. Update `close_bids()` ordering in `game/engine_base.py`.
2. Add targeted engine test in `tests/test_engine.py`.

## Weird variation checklist

- Tie-break changed from first-bid-wins to random or last-bid-wins.
- House auction removed or repeated each orbit.
- Seller required to auction exactly one card.
- Seller required to include at least one card above threshold value.
- Mandatory minimum bid.
- Bid cap per turn or per round.
- Pot carries over across rounds.
- Forced objective changes (for example top-2 points league scoring).

For each new variant:

- encode in `RuleProfile` when possible.
- if not possible, patch engine + tests first, then run fast champion recompute.

## Operator run commands

Start backend:

```bash
uv run uvicorn game.api:app --reload --host 0.0.0.0 --port 8000
```

Start HUD:

```bash
cd web
pnpm install
pnpm dev --host 0.0.0.0 --port 4173
```
