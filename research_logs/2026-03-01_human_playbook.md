# Human playbook for Sold 'Em

Local timestamp: 2026-03-01 05:24:10 PST

## Core principle

In this rule set, overpaying in first-price auctions is the biggest leak. The current best system strategy wins by extracting value while staying selective on purchases.

## Default objective for tomorrow

- If standings are close or you need stability: use `robustness`.
- If you need to climb aggressively in ~10 games: use `first_place`.
- Default if uncertain: `ev`.

Current objective-specific champion set:

- `ev`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- `first_place`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`
- `robustness`: `seller_extraction:opportunistic_delta=4400,reserve_bid_floor=0.02,sell_count=2`

Recent EC2 confirmation path:

- Old champion (`reserve_bid_floor=0.086`) won 777/864 scenarios in earlier distributed runs.
- Param sweep run `20260301-024646` found `reserve_bid_floor=0.06` variants with strong positive delta over old champion.
- Validation run `20260301-030400` with expanded pool gave 210/216 wins to the two `reserve_bid_floor=0.06` variants.
- Expanded-pool run `20260301-031824` and targeted confirmation sweep `20260301-033100` upgraded final recommendation to `3300/0.029/2`.
- Focused evolution and distributed candidate run (`20260301-044713`, `20260301-045734`) surfaced `4400/0.02/2` as strongest broad challenger.
- Param sweep run `20260301-050721` (108 scenarios vs `3300/0.029/2`) confirmed:
- `4400/0.02/2` mean delta `+5.13`, wins/losses `77/31`
- horizon-10 mean delta `+8.03`, wins/losses `30/6`
- horizon-10 objective deltas vs prior champion:
- `ev`: `+8.36`
- `first_place`: `+0.0586`
- `robustness`: `+15.67`
- Promotion artifacts:
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-050721.json`
- `research_logs/experiment_outputs/horizon10_confirmation_20260301-050721.json`

## Turn-by-turn guidance

### When selling

- Prefer auctioning 2 cards.
- Offer cards that are attractive to others but not central to your best 5-card hand.
- Early rounds: prioritize extraction from aggressive bidders.
- If table is passive, reduce quality of offered cards and preserve hand equity.

### When bidding

- Default to low/zero bids unless the card materially upgrades your final hand.
- Avoid ego bidding wars; first-price auctions punish this heavily.
- Late orbit can justify slightly higher bids if the card directly completes strong structure.
- Keep stack discipline. Never chase marginal upgrades with high bids.

### When choosing won card

- Choose the card with the largest improvement to your best 5-card subset.
- Do not choose speculative cards that do not immediately improve your showdown strength.

## Opponent exploitation

- Track per-player aggression (average bid / stack).
- Against high-aggression players:
- sell more attractive bundles to capture transfer value
- tighten your own buy threshold
- Against low-aggression tables:
- slightly lower buy threshold on high-impact cards
- expect lower sell profits

## Correlation and social effects

- Watch for "respect pairs" where two players avoid bidding against each other.
- Watch for herd behavior where one player's bid level predicts another's.
- If detected, expect distorted auction prices and prioritize exploiting uncrowded turns.

## Fast operational workflow

1. Enter current state in HUD.
2. Use objective mode aligned with leaderboard needs.
3. Take `action_first` output as baseline action.
4. Check `top3` for alternatives when social context suggests deviation.
5. Log notable behavior using session events for profile updates.
