# Baseline rule assumptions

Local timestamp: 2026-03-01 01:45:00 PST

`RULES.md` is the source of truth. This file records the current implementation assumptions so day-of patches can be applied quickly.

## Canonical baseline

- 5 players per table.
- Deck is 50 cards: values `1-10` and suits `C D H S X`.
- Each player starts with 5 private cards and 200 chips.
- Ante is 40 chips per player.
- Round uses 3 orbits by default.
- House auction is first and winner pays into pot.
- House winner becomes first seller.
- Player auctions are first-price and winner pays seller.
- Tie break on equal bids is earliest bid timestamp.
- Seller cannot bid own auction by default.
- Multi-card selling is enabled by default.
- Showdown evaluates best 5-card subset of current holdings.
- Default pot distribution is winner-takes-all.

## Ranking policy default

- Default ranking policy is rarity-based (`rarity_50`).
- Verified exact 50-card combinatorics (`50 choose 5 = 2,118,760`) match `CATEGORY_RARITY_COUNTS_50` in `game/utils.py`.
- Rarity order is:
  - `five_kind`
  - `straight_flush`
  - `flush`
  - `four_kind`
  - `full_house`
  - `straight`
  - `three_kind`
  - `two_pair`
  - `high_card`
  - `one_pair`

## Variant switches implemented now

- `seller_can_bid_own_card`
- `allow_multi_card_sell`
- `hand_ranking_policy`
- `pot_distribution_policy` (`winner_takes_all`, `top2_split`, `high_low_split`)
- `n_orbits`, `ante_amt`, `start_chips`

## Built-in profiles

- `baseline_v1`
- `standard_rankings`
- `seller_self_bid`
- `top2_split`
- `high_low_split`
- `single_card_sell`
