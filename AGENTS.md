- When writing markdown docs, use sentence case for headers
- Use light mode
- There might be variants, so it's best to build an engine that takes these into account. In particular, we should account for:
  - Community cards (of any number, deployed at any time)
- Might LMPs (language model programs) be useful here?
- Use `uv` and `pnpm` and `sveltekit`

## Notes

- We are playing against humans. It may be beneficial to keep profiles of players (their history) and take this into account during the game.
- It's possible that there are bad externalities. For example, two players might "really respect each other" and correlate in ways that are bad for everyone else.
- When running simulations, it's important to simulate this kind of correlation.

## Strategy (roughly)

- Calculate P(win given win auction) - P(win given lose auction) as delta P
- delta P \* pot tell us the "fair value" for how much we should bid.
  - If you win the auction, "you face adversity."
