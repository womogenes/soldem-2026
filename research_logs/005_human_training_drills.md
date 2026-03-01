# Human training drills for day-of execution

Local time: 2026-03-01 02:25 PST

## Purpose

Convert simulation findings into repeatable human decisions under the 10-second bidding clock.

## Pre-game setup (5 minutes)

1. Run API and HUD.
`uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`
`pnpm -C web dev --host`

2. In HUD:
- objective: `ev`
- click `Use objective champion`
- confirm strategy is `equity_evolved_v1`

3. Keep this fallback ladder ready:
- default: `equity_evolved_v1`
- exact baseline + first-place objective: `meta_switch`
- high-ante winner-takes-all (`n_orbits>=3` and (`ante/start>=0.26` or `ante>=50`)): `pot_fraction`
- sprint winner-takes-all (`n_orbits<=2`, low stack): `pot_fraction`
- passive high-confidence table read + first-place objective: `pot_fraction`

## Drill block A: fast data entry discipline (10 minutes)

Goal: under 8 seconds from new auction info to actionable recommendation.

1. Enter state for 20 synthetic spots quickly.
2. For each spot, log one event (`bid` or `auction_result`) and request recommendation.
3. Track average cycle time.
4. If over 8 seconds, reduce input clutter:
- only update changed stacks/cards
- avoid unnecessary notes mid-orbit

Success metric: 80% of cycles completed under 8 seconds.

## Drill block B: table-read adaptation (10 minutes)

Goal: trust but verify switching rules.

1. Simulate 12 bid events with low bids/zeros.
2. Confirm HUD `table_read.mode` moves to `passive` and recommended preset updates.
3. Simulate a seller-winner pair repeatedly in `auction_result`.
4. Confirm `table_read.mode` moves to `correlated_pair` and switch to sniper profile.
4. Confirm `table_read.mode` moves to `correlated_pair` and use auto preset (`correlated_table`).
5. Confirm `resolved_champion_reasons.first_place` is sensible for the current rules (`baseline_first_place_meta_exact`, `high_ante_pressure_first_place`, etc.).

Success metric: correct mode transitions without confusion.

## Drill block C: objective switching protocol (10 minutes)

Goal: avoid over-switching.

Rule:
1. Stay on `ev` for first two games unless behind materially.
2. Move to `first_place` only if:
- leaderboard requires upside, and
- table is not chaotic/aggressive, or a known first-place trigger is active.
3. Return to `ev` immediately after recovery.

Success metric: objective switches are deliberate, not reactive to one bad hand.

## Mental checklist per auction (under 10 seconds)

1. Is this spot high delta for my hand or a trap overpay?
2. Does current table-read suggest conservative or sniper behavior?
3. Is my objective still correct (`ev` vs `first_place`)?
3. If on `first_place`, is a trigger active (baseline meta / high-ante WTA / sprint WTA / passive high-confidence)?
4. Can I win this auction without violating stack discipline?

## Critical anti-tilt rules

1. No revenge bidding after losing an auction.
2. If two consecutive uncertain spots happen, default to conservative cap.
3. Do not switch to `pot_fraction` unless explicitly in catch-up mode.
3. Do not force `pot_fraction` unless objective/trigger conditions support it.

## Final 5-minute rehearsal before game

1. Apply actual announced rule profile with `scripts/day_of_patch.py`.
2. Run three mock auctions end-to-end.
3. Verify `First-place routing cues` and `resolved_champion_reasons` match expected triggers.
