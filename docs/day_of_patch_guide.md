# Day-of patch guide

Local timestamp: 2026-03-01 03:10:00 PST

Goal: apply unknown rule changes in under 2 minutes.

## Two-minute patch flow

1. Ensure API is running.

```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

2. Apply profile and/or overrides.

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

3. Verify active profile.

```bash
curl -s http://127.0.0.1:8000/session/state
```

4. Continue play in HUD.

When profile names match built-in variants, champion defaults auto-switch based on the profile/objective lookup.

## Common patch recipes

### Seller can bid own auction

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"seller_can_bid_own_card": true}'
```

### Single-card selling only

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"allow_multi_card_sell": false}'
```

### Standard poker-style ranking order

```bash
uv run python scripts/apply_rule_patch.py --profile standard_rankings
```

### Top-two split payout

```bash
uv run python scripts/apply_rule_patch.py --profile top2_split
```

### High-low split payout

```bash
uv run python scripts/apply_rule_patch.py --profile high_low_split
```

### Ante/orbit changes

```bash
uv run python scripts/apply_rule_patch.py --profile baseline_v1 --overrides '{"ante_amt": 30, "n_orbits": 4}'
```

## Weird variation playbook

- Apply closest override immediately so advisor remains usable.
- Log a note event with exact rule text.
- After the round, add a new profile in `game/rules.py` and restart API.

## Champion fallback map under variants

Risk-adjusted defaults (EV-constrained) from `research_logs/experiment_outputs/rule_profile_validation_long.json`.
Raw objective-metric winners are exported in `research_logs/champion_lookup_from_rule_profile_validation_long.json` and include higher-variance first-place picks.

- `baseline_v1`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
- `standard_rankings`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
- `seller_self_bid`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
- `top2_split`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
- `high_low_split`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
- `single_card_sell`: `market_maker_tight` for `ev` and `first_place`; `regime_switch_robust` for `robustness`.
