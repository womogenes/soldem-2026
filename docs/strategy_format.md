# Strategy file format

Local timestamp: 2026-03-01 01:45:00 PST

Strategies can be referenced by built-in tag or Python file path.

## Built-in tags

Current built-ins include:

- `market_maker`
- `conservative_ultra`
- `conservative`
- `elastic_conservative`
- `conservative_plus`
- `mc_edge`
- `pot_fraction`
- `seller_profit`
- `adaptive_profile`
- `random`
- `bully`
- `delta_value`

## External strategy interface

A Python strategy file must expose either:

- `build()` returning a strategy object, or
- `Strategy` class instantiable with no args.

The strategy object must provide:

- `tag: str`
- `on_round_start(ctx)`
- `choose_sell_indices(ctx) -> list[int]`
- `bid_amount(ctx) -> int`
- `choose_won_card(ctx) -> int`

See `strategies/examples/minimal_strategy.py` for a minimal external strategy.

## Evaluate five strategies with compact logging

```bash
uv run python scripts/run_match.py \
  market_maker conservative_ultra conservative elastic_conservative mc_edge \
  --n-games 1000 \
  --seed 42 \
  --compact-log research_logs/sim_logs/match_001.jsonl \
  --out research_logs/sim_logs/match_001_summary.json
```

## Population tournament for discovery

```bash
uv run python scripts/run_population.py \
  market_maker conservative_ultra conservative elastic_conservative conservative_plus mc_edge \
  pot_fraction seller_profit adaptive_profile random bully delta_value \
  --n-matches 220 \
  --n-games-per-match 10 \
  --seed 2026 \
  --out research_logs/experiment_outputs/candidates_ev_none.json
```
