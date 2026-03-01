# Strategy plugin format

## Local timestamp

2026-03-01 01:45:09 PST

## Goal

Allow strategy experimentation with:

- stable unique tags
- parameterized built-in specs
- file-based custom strategies
- direct five-strategy seat assignment for match rollouts

## Built-in strategy spec format

Use:

`<tag>` or `<tag>:<param>=<value>,<param>=<value>`

Examples:

- `conservative`
- `prob_value:bid_scale=1.05,sell_count=2,min_delta_to_bid=300`
- `seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2`

Loader behavior:

- `strategies/loader.py` parses and type-coerces params.
- Canonical tag is normalized and stored (sorted param keys) for stable identity in logs and database records.

## File-based strategy format

Strategy files can be passed directly by path.

A file must export either:

- `build()` returning a strategy instance, or
- `Strategy` class with methods:
- `on_round_start(ctx)`
- `choose_sell_indices(ctx)`
- `bid_amount(ctx)`
- `choose_won_card(ctx)`

If no explicit `tag` attribute is provided, the filename stem is used.

## Five-seat rollout examples

### Mixed built-ins and parameterized specs

```bash
uv run python scripts/run_match.py \
  "seller_extraction:opportunistic_delta=4000,reserve_bid_floor=0.086,sell_count=2" \
  "conservative" \
  "bully" \
  "risk_sniper:trigger_delta=2400" \
  "prob_value:bid_scale=1.05,sell_count=2,min_delta_to_bid=300" \
  --n-games 100 --seed 42 --compact-log research_logs/compact_match.jsonl
```

### Five Python files

```bash
uv run python scripts/run_match.py \
  strategies/custom/seat0.py \
  strategies/custom/seat1.py \
  strategies/custom/seat2.py \
  strategies/custom/seat3.py \
  strategies/custom/seat4.py \
  --n-games 100 --seed 42 --compact-log research_logs/compact_match.jsonl
```

## Compact logging format

- `scripts/run_match.py --compact-log <path>` writes one JSON line per game.
- Fields are compact (`g`, `sd`, `pnl`, `rk`, `w`, `pp`) to keep history files small.
