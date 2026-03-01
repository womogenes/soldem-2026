# Strategy file format

Local timestamp: 2026-03-01 01:26 PST

This repository supports strategy specs as either:

- Built-in tags (`random`, `pot_fraction`, `delta_value`, `conservative`, `bully`, `seller_profit`, `adaptive_profile`)
- Python file paths (for custom external strategies)

## Required interface

A strategy file must export either:

- `build()` returning a strategy object, or
- `Strategy` class instantiable with no arguments.

The object should define:

- `tag: str` unique strategy identifier
- `on_round_start(ctx)`
- `choose_sell_indices(ctx) -> list[int]`
- `bid_amount(ctx) -> int`
- `choose_won_card(ctx) -> int`

See example: [minimal_strategy.py](/home/willi/coding/trading/soldem-2026/v2/strategies/examples/minimal_strategy.py).

## Evaluate five strategies directly

```bash
python scripts/run_match.py \
  strategies/examples/minimal_strategy.py \
  random pot_fraction delta_value conservative \
  --n-games 1000 \
  --seed 42 \
  --compact-log research_logs/sim_logs/match_001.jsonl \
  --out research_logs/sim_logs/match_001_summary.json
```

## Run population tournament

```bash
python scripts/run_population.py \
  random pot_fraction delta_value conservative bully seller_profit adaptive_profile \
  --n-matches 200 \
  --n-games-per-match 10 \
  --seed 11 \
  --out research_logs/tournaments/pop_001.json
```
