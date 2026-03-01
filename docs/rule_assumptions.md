# Baseline rule assumptions

Local timestamp: 2026-03-01 01:18 PST

This project treats [RULES.md](/home/willi/coding/trading/soldem-2026/v2/RULES.md) as authoritative. The following assumptions are explicit so day-of patches can be applied quickly.

## Canonical baseline

- 5 players per table.
- Deck is fixed to 50 cards: values 1-10, suits `C D H S X`.
- Each player is dealt 5 private cards.
- Starting chips are 200.
- Ante is 40 per player per round.
- There are 3 orbits per round by default.
- House auction occurs first with one face-up card; winner pays into pot and becomes first seller.
- For player auctions, winner pays seller directly (first-price auction).
- Tie breaks on bids are earliest timestamp first.
- By default, seller cannot bid on own auction.
- Multi-card selling is enabled by default.
- Showdown uses best 5-card subset from each player’s current cards.
- Pot distribution default is winner-takes-all (split on exact tie).

## Ranking policy default

- Default ranking policy is rarity-based for this 50-card deck.
- Rarity order used by default:
  - five-kind
  - straight flush
  - flush
  - four-kind
  - full house
  - straight
  - three-kind
  - two pair
  - high card
  - one pair
- A standard poker-like ranking with five-kind on top is available via `standard_plus_five_kind`.

## Variant switches supported now

- `seller_can_bid_own_card`
- `allow_multi_card_sell`
- `hand_ranking_policy`
- `pot_distribution_policy` (`winner_takes_all`, `top2_split`, `high_low_split`)
- `n_orbits`, `ante_amt`, `start_chips`

## Built-in rule profiles

- `baseline_v1`
- `standard_rankings`
- `seller_self_bid`
- `top2_split`
- `high_low_split`
- `single_card_sell`
