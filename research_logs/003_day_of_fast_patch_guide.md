# Day-of fast patch guide

Local time: 2026-03-01 01:58 PST

## Goal

Patch rule variations and keep advisor strategy alignment in under 2 minutes.

## 2-minute patch flow

1. Start API if not running.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Apply a known preset (one command).
`uv run python scripts/day_of_patch.py --preset high_low_split`

3. If the host announces custom values, add explicit overrides.
`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4,"ante_amt":30}'`

4. Confirm resolved champions from output.
Expected fields: `resolved_champions.ev`, `resolved_champions.first_place`, `resolved_champions.robustness`.

5. Refresh HUD and use `Use objective champion` button.

## Preset map

- `baseline`: default published rules.
- `top2_split`: split between top two hand ranks.
- `high_low_split`: split between highest and lowest hand ranks.
- `single_card_sell`: seller can only auction one card.
- `seller_self_bid`: seller can bid on own auction.
- `standard_rankings`: standard poker ordering plus five-of-a-kind.
- `weird_short_stack`: stress mode with short stacks and fewer orbits.
- `weird_long_game`: stress mode with deeper stacks and more orbits.
- `weird_6p`: six-player table assumption.

## Champion policy used by API

- Default EV and robustness: `conservative_plus`.
- First-place mode: `equity_sniper_ultra`.
- Automatic shifts:
  - `high_low_split` or seller self-bidding environments bias to `conservative_plus`.
  - `top2_split`, standard ranking policy, or single-card selling bias to `equity_sniper_ultra`.

## Fast fallback if rules are unknown

1. Use baseline preset first.
2. Enter exact overrides from host announcement.
3. Keep objective on `ev` for first two games to calibrate table behavior.
4. Move to `first_place` only if table is clearly passive or you need catch-up variance.

## Weird-variation checklist

1. Player count changed (`n_players != 5`): patch profile immediately and run a 20-table smoke benchmark if time allows.
2. Ante/start stack changed: patch `ante_amt` and `start_chips`; this shifts bid caps materially.
3. Orbits changed: patch `n_orbits`; later-orbit urgency in bidding depends on this.
4. Pot distribution changed: patch `pot_distribution_policy`; this changes champion preference.
5. Ranking policy changed: patch `hand_ranking_policy`; this changes card delta value and strategy strength.
6. Seller self-bid changed: patch `seller_can_bid_own_card`; this changes auction competition intensity.

## If a totally new rule appears

1. Patch what is representable in `RuleProfile` immediately via overrides.
2. Log the missing dimension in `research_logs/001_night_rollout_log.md`.
3. For unsupported mechanics (for example community cards), use HUD in metric mode and manually weight recommendations with conservative bid caps until engine patch lands.
