# Day-of fast patch guide

Local time: 2026-03-01 01:58 PST

## Goal

Patch rule variations and keep advisor strategy alignment in under 2 minutes.

## 2-minute patch flow

0. Optional quick preflight (API + PocketBase reachability).
`bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --pb-url http://18.204.1.6:8090`

1. Start API if not running.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`

2. Apply a known preset (one command).
`uv run python scripts/day_of_patch.py --preset high_low_split`

3. If the host announces custom values, add explicit overrides.
`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4,"ante_amt":30}'`

4. Optional: lock manual champions in same command.
`uv run python scripts/day_of_patch.py --preset top2_split --set-ev equity_evolved_v1 --set-first-place equity_evolved_v1 --set-robustness equity_evolved_v1`
This sets API `dynamic_resolution_enabled=false` so manual champions stay fixed.

5. Optional: keep dynamic resolver active while updating champion defaults.
`uv run python scripts/day_of_patch.py --preset baseline --set-ev equity_evolved_v1 --set-first-place meta_switch --set-robustness equity_evolved_v1 --keep-dynamic`

6. Confirm resolved champions from output.
Expected fields: `resolved_champions.ev`, `resolved_champions.first_place`, `resolved_champions.robustness`.

7. Refresh HUD and use `Use objective champion` button.
8. After logging a few auctions/bids, use `Use auto table read preset` to adapt to observed table style.

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

- Default EV and robustness: `equity_evolved_v1`.
- First-place mode:
  - `baseline_v1`: `meta_switch`
  - other built-in variants: `equity_evolved_v1`.
- Dynamic table-read shifts:
  - `passive` with high confidence and first-place objective: may choose `pot_fraction`.
  - sprint rules (`n_orbits<=2` and `start_chips<=150`) with first-place objective: choose `pot_fraction`.
  - all other EV/robustness modes stay on `equity_evolved_v1`.

## Fast fallback if rules are unknown

1. Use baseline preset first.
2. Enter exact overrides from host announcement.
3. Keep objective on `ev` for first two games to calibrate table behavior.
4. Move to `first_place` only if table is clearly passive or you need catch-up variance.

## Optional quick solver during warmup

If there is enough time for a small empirical pass (typically a few minutes), run:

`uv run python scripts/quick_variant_hero_solver.py --rule-profile baseline_v1 --rule-overrides-json '{"n_orbits":4}' --n-tables 12 --n-games 8 --out research_logs/experiment_outputs/live_variant_probe.json`

Then set manual champions from `objective_winners` if you want to lock them:

`uv run python scripts/day_of_patch.py --preset baseline --overrides-json '{"n_orbits":4}' --set-ev <tag> --set-first-place <tag> --set-robustness <tag>`

## One-command autosolve and patch

Use this when host-announced rules are clear and you want an empirical lock in one command:

`uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '{"n_orbits":2,"start_chips":140,"ante_amt":30}' --n-tables 12 --n-games 8 --seed 42`

Notes:
- runs the quick hero solver under the specified variant,
- applies profile/overrides to API,
- applies prior guardrails by default so low-sample noisy flips are ignored unless margin is meaningful,
- sets champions and locks manual mode by default.
- observed runtime on this machine with defaults (`n_tables=12`, `n_games=8`): about `22.9s`.

To keep dynamic resolution active after setting winners:

`uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '{"n_orbits":2,"start_chips":140,"ante_amt":30}' --keep-dynamic`

To disable guardrails and trust raw solver winners:

`uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '{"n_orbits":2,"start_chips":140,"ante_amt":30}' --no-prior-guardrail`

Default first-place guardrail is `--first-gap 0.07`.
To make it even more conservative, raise further:

`uv run python scripts/day_of_autosolve_patch.py --rule-profile top2_split --first-gap 0.10`

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
