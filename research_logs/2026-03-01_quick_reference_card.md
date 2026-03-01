# Sold 'Em quick reference card

Local timestamp: 2026-03-01 04:35:52 PST

## Primary strategy

- Default for `ev`, `first_place`, and `robustness`:
- `seller_extraction:opportunistic_delta=3300,reserve_bid_floor=0.029,sell_count=2`

## Why this is current default

- Expanded EC2 run `20260301-031824` surfaced `3300/0.029/2` as dominant winner.
- Targeted EC2 confirmation run `20260301-033100` found no challenger with positive mean delta vs this champion.

## Turn actions

- Sell phase:
- default to selling 2 cards
- choose cards that look valuable to others but preserve your strongest 5-card core
- Bid phase:
- avoid marginal bids; first-price overbidding is the main leak
- bid up only for immediate hand-improving cards
- Choose phase:
- take the card with maximum immediate showdown improvement

## Objective switch guidance

- If you need low-variance leaderboard defense, keep default champion and use `robustness`.
- If you need upside in final games, keep default champion and use `first_place`.

## Day-of fastest commands

Load latest champions into API:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path": null}'
```

Print latest champion artifact from CLI:

```bash
uv run python scripts/print_latest_champions.py
```

## Active database endpoint

- PocketBase (active synced node): `http://3.236.115.133:8090`
