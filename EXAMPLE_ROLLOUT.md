# EXAMPLE_ROLLOUT

## Here is a step-by-step example rollout of a single round of Sold 'Em to help illustrate the mechanics of the game.

## Setup and Ante

Imagine a table of 5 players: Alice, Bob, Charlie, Diana, and Eve.

- Starting State: Each player starts with 200 chips and is dealt 5 random cards from the 50-card deck (which includes the special Citadel suit).
- The Ante: Every player pays a 40-chip ante. The main pot now has 200 chips. Every player's stack is reduced to 160 chips.

## The House Auction

The round begins with a special "house auction" to determine who goes first and to add more chips to the pot.

- A random card is drawn from the deck (e.g., the 8 of Citadel).
- All players have 10 seconds to submit a private, blind bid.
- Let's say the bids are:
  - Alice: 20 chips
  - Bob: 15 chips
  - Charlie: 30 chips
  - Diana: 0 chips
  - Eve: 10 chips
- Outcome: Charlie wins the house auction. He pays 30 chips directly into the main pot, which now holds 230 chips. Charlie's stack is down to 130 chips, but he adds the 8 of Citadel to his hand and earns the right to host the first player auction.

## Orbit 1: Player Auctions

Now the regular orbits begin. In each orbit, players take turns hosting an auction. There are usually 3 orbits, meaning each player will host 3 auctions per round.  
Turn 1: Charlie's Auction

- Because Charlie won the house auction, he goes first. He looks at his hand and decides to auction off two cards: the 3 of Hearts and the 4 of Spades.
- The other four players submit their private bids within 10 seconds.
- Let's say Bob bids 25 chips, which is the highest.
- Outcome: Bob wins the auction. Bob chooses to keep the 4 of Spades and the unchosen card goes back to Charlie. Bob pays 25 chips directly to Charlie.
- Bob's stack is now 135 (160 \- 25), and Charlie's stack is 155 (130 \+ 25).

Turn 2: Diana's Auction

- The turn passes clockwise to Diana. She puts up the 9 of Diamonds.
- Everyone bids. Alice bids 40 chips and wins.
- Outcome: Alice pays 40 chips to Diana. Alice adds the 9 of Diamonds to her hand.
- Alice's stack is 120; Diana's stack is 200\.

Remaining Turns

- The turns continue around the table (Eve, Alice, Bob) until everyone has hosted one auction. This completes Orbit 1\.

## Orbits 2 and 3

- The game continues for two more full orbits. Players continue to buy and sell cards to build the strongest possible 5-card poker hand.
- Remember, players are trying to build the best hand and manage their chips. Selling a great card might give you a lot of chips, but it could ruin your hand.
- The ultimate objective of the game is to maximize your PnL, which can be achieved by trying to build the best hand or simply manage their chips.

## Showdown

After all 3 orbits are complete, the auction phase ends.

- Reveal: All players who have at least five cards reveal their final five-card hands. This best 5-card subset of each player’s hole cards is displayed and used to determine who wins the pot.
- Evaluating Hands: The hands are ranked according to standard poker rules, adjusted for the 5-suit deck (which might make flush probabilities different, for example). The standard variant for this game re-ranks different 5-card poker hands in terms of rarity, and this ordering is used for showdown. However, different rankings variants may be possible in the game.
- Let's say Alice managed to build a straight (5, 6, 7, 8, 9), which beats everyone else's hands.
- Payout: In a standard winner-takes-all variant, Alice wins the entire main pot (which was 230 chips from the ante and house auction, plus any other house actions if applicable).
- Calculating PnL: At the end of the round, each player calculates their Profit and Loss (PnL). This is their final chip stack plus any pot winnings, minus their starting 200 chips.
  - If Alice’s stack ended at 100 chips before the showdown, then with the 230 chip pot, her final stack is 330\. Her PnL for the round is \+130.

## Next Round

Stacks are reset to 200 for the next round, but Alice carries her \+130 PnL forward on the game's overall leaderboard. The game continues for the designated number of rounds, and the player with the highest total PnL at the end is the overall winner.

## Variants

All assumptions here could be challenged in variations and you should prepare for this. Investigate different changes to the rules (however wild they may be) and evaluate strategies under that new paradigm using the same process.
