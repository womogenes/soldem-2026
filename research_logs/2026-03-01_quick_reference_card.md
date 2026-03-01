# Sold 'Em quick reference card

Local timestamp: 2026-03-01 06:53:34 PST

## Primary strategies

- `ev`: `seller_extraction:opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2`
- `first_place`: `seller_profit`
- `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`

## Why this is current default

- EC2 param sweep `20260301-050721` vs prior champion `3300/0.029/2`:
- mean delta `+5.13` and wins/losses `77/31`.
- 10-game extraction from same run:
- mean delta `+8.03` and wins/losses `30/6`.
- EC2 distributed run `20260301-053816` (human-like pool):
- first-place counts favored `seller_profit`.
- robustness counts favored `4500/0.02/2`.
- EC2 distributed run `20260301-061228` (human-focused pool, `n_matches=360`):
- `ev` winner count favored `5400/0.032/2`.
- first-place winner count favored `bully`, but strength metrics favored `seller_profit`.
- robustness winner count slightly favored `4400/0.02/2` over `4500/0.02/2`.
- merged promotion artifact across `053816` + `061228` (432 scenarios):
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-062400-merged.json`.
- quick exploitability sweep vs `5400/0.032/2`:
- `research_logs/experiment_outputs/param_sweep_20260301-063621/aggregate_summary.json`.
- conservative fallback artifact:
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`.
- final merged pre-7am promotion across three human-focused distributed runs:
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-065230-merged3.json`.

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

- If you need low-variance leaderboard defense, use `robustness` strategy `4400/0.02/2`.
- If you need upside in final games, use `first_place` strategy `seller_profit`.

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
