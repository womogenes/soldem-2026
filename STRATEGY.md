# EV-Maximizing Strategy for Sold ’Em

## How the game pays you

Sold ’Em is best understood as two games stapled together: (1) a **sequential first-price auction market** for individual cards, and (2) a **showdown** where a pot is awarded based on poker-hand strength. The end-of-round “truth” is simple: you finish with some number of chips, and that difference from your starting stack determines your per-round PnL (and your cumulative PnL across rounds, since stacks reset). That structure pushes you toward a single core objective: **treat every bid and every sale as an investment decision whose payoff is “change in expected showdown winnings” plus “change in expected future trading power,” minus “chips you give up.”** (In game modes that split pots, replace “showdown winnings” with “expected share of the split.”)

A practical implication of your rules is that (after the house auction), most auction payments are **player-to-player transfers**. Those transfers don’t change the total chips at the table, but they absolutely change _your_ chips—so the only reason to buy a card is that the card’s presence in your eventual hand set increases your expected showdown return (or enables a later profitable sale). That’s exactly the economic setting studied in sequential-auction and trading-agent research: goods with **combinatorial value** (cards are worth more in the right bundle) traded over time with strategic opponents. citeturn11view2turn5view3turn5view6

## What auction theory says that matters in Sold ’Em

### First-price auctions demand “value-first,” then shading (or “dropout-at-value”)

Your rules specify a **first-price auction** (highest bidder wins and pays their own bid). That’s the classic environment where bidding your full value is generally irrational because it can drive your surplus to zero if you win at your exact value. citeturn5view0turn6view0

In the canonical “independent private values” model with symmetric bidders, theory predicts **bid shading**: you bid below your value, and the shaded amount depends on how many competitors you face. A widely taught special case (uniform values) yields the simple rule of thumb: bid about \((n-1)/n\) of value, where \(n\) is the number of bidders. citeturn6view1  
With 5 players at a table, the “textbook” shading heuristic would be ~80% of value _if_ everyone is symmetric and valuations are i.i.d.—conditions that are not literally true in Sold ’Em, but the directional lesson (“don’t auto-bid your max”) is still important. citeturn6view1turn5view0

However, many digital/card-game “first-price” auctions are run as an **open ascending** process where players can keep raising until they drop out. In independent-private-values settings, standard models of ascending auctions imply a “stay in until your value, then drop” logic that behaves much closer to a second-price outcome (you tend to win near the second-highest willingness to pay). citeturn6view3turn12view0  
So, your real-world best practice is:

- If bidding is **open ascending**: treat your “maximum willingness to pay” as a hard stop and don’t exceed it.
- If bidding is **effectively sealed** (you must commit a number and live with it): shade below max, and shade more when many opponents plausibly want the card.

### Sold ’Em has interdependent values and resale—two big complications

In your game, a card’s value is rarely “just my taste.” It depends on (a) what it completes for you, (b) what it completes for an opponent if you _don’t_ win it, and (c) what the card can be resold for later given evolving needs. Auction theory explicitly studies settings where payoffs depend on others and on informational signals—often labeled **interdependent values**—and shows that auction format and information revelation materially affect outcomes. citeturn12view1turn12view0

You also effectively have **resale**: if you win a card now, you may auction it later. Formal models show resale can change incentives sharply; for example, even in formats where “bid your value” is normally dominant, resale can break that logic, and equilibrium behavior can shift because players anticipate later trading opportunities. citeturn5view5

For your preparation, the takeaway is not “memorize equilibrium proofs.” It’s this: **your system must value a card as an asset with (i) use value, (ii) deny value, and (iii) resale/option value.** That is exactly the framing used by automated bidding agents designed for sequential auctions with complementarities. citeturn11view2turn5view3turn10view2turn5view5

### Sequential-auction research gives you an actionable optimality principle

A very direct, game-ready result from the agent literature is: in sequential auctions, under common modeling assumptions (risk-neutral utility, known order of goods, probabilistic future prices), **expected marginal utility bidding is an optimal policy**: bid the difference between your expected value _with_ the item and _without_ the item, given what remains to be auctioned. citeturn11view2turn10view2  
This is the cleanest theoretical foundation for a Sold ’Em “solver mindset,” because your entire problem is “buy or don’t buy this card, knowing more auctions are coming.” citeturn11view2turn5view3turn10view2

### Order and timing effects are real in sequential markets

Empirically, sequential auctions often exhibit price trends (famously, **declining prices** across the sequence), even when simple theory suggests flat paths. Multiple studies document and discuss this “declining price anomaly.” citeturn10view3turn5view7  
For Sold ’Em, where stacks are limited (200 chips) and the number of orbits is small, the practical analog is: **budgets get allocated early, information gets revealed over time, and late auctions can be either bargains (because players are “done shopping”) or spikes (because someone is desperate for the last piece).** Sequential-auction models also emphasize that what is revealed between rounds changes later bids. citeturn5view6turn10view3

## Hand value in your 50-card, five-suit deck

Because your deck is nonstandard (5 suits × ranks 1–10), you should not rely on “poker intuition” calibrated to a 52-card deck. You still use familiar hand categories (pair, two pair, etc.), but the **frequency and leverage** of each category changes.

Standard references define poker hands and rank categories, and note that “five of a kind” is normally only possible with wild cards because standard decks have four suits. citeturn14view1turn11view0turn11view1  
In your deck, **five-of-a-kind becomes physically possible without wild cards** (because there are five suits). Whether it exists as a distinct category (and where it ranks) is a rules question you should confirm, but if allowed it is natural to place it above straight flush, consistent with how five-of-a-kind is treated in common wild-card hand-rank references. citeturn11view0turn14view1

### Baseline frequencies for random 5-card hands in your deck

If a player ends showdown choosing exactly 5 cards from their holdings, these baseline frequencies matter because they determine how “rare” each made hand is (and thus how much equity shifts when you buy a card that completes one). In your 50-card deck, there are \(\binom{50}{5}=2{,}118{,}760\) distinct 5-card hands, and the exact category counts (assuming standard high-hand ranking with a five-of-a-kind category available) are:

| Hand category                 | Exact count | Probability |
| ----------------------------- | ----------: | ----------: |
| Five of a kind                |          10 |    0.00047% |
| Straight flush                |          30 |    0.00142% |
| Four of a kind                |       2,250 |      0.106% |
| Full house                    |       9,000 |      0.425% |
| Flush (not straight flush)    |       1,230 |      0.058% |
| Straight (not straight flush) |      18,720 |      0.884% |
| Three of a kind               |      90,000 |       4.25% |
| Two pair                      |     180,000 |       8.50% |
| One pair                      |   1,050,000 |       49.6% |
| High card                     |     767,520 |       36.2% |

These numbers are not “flavor”; they tell you what your auctions will feel like. In particular, **one pair is extremely common**, and **full houses and above are very rare** in a pure 5-card world—so any card that credibly upgrades you into “full house+ territory” is usually worth a lot of pot equity.

### If you can hold more than five cards, extra cards are worth a lot early

Many community-card poker games explicitly let players form the best five-card hand from a larger set (e.g., in Texas hold ’em you can form the best five-card hand from seven cards total). citeturn5view9turn14view0  
If Sold ’Em similarly allows you to use _any_ five cards from all cards you hold (plus community cards in relevant rounds), then buying extra cards has a compounding effect: it increases the chance you can assemble at least a straight, flush, or full house by showdown.

Under that “best five from N” assumption (and no community cards), quick Monte Carlo estimates in your 50-card deck suggest:

- With 5 cards: \(P(\text{straight or better}) \approx 1.5\%\)
- With 8 cards: \(P(\text{straight or better}) \approx 33.8\%\)
- With 10 cards: \(P(\text{straight or better}) \approx 71.9\%\)

This is why your preparation should explicitly answer one rules question: **Is showdown the best five from everything you hold, or strictly five cards?** Your entire valuation engine depends on it.

## A decision rule that actually maximizes EV in play

The research-backed core is “expected marginal utility,” but you need it translated into something you can execute at a table.

### Step one: keep a public ledger and infer “who wants what”

Your strongest edge in Sold ’Em is informational discipline: track every auctioned card and every winner. Sequential-auction theory highlights that information revealed between rounds materially affects later bidding. citeturn5view6turn12view0  
In practice, you want a running model of each opponent:

- what suits they are accumulating,
- what ranks they are concentrating,
- whether their bids suggest “use value” (building a hand) or “speculative/resale” behavior.

This inference matters because Sold ’Em is not a clean private-values auction; payoffs can depend on others, which is precisely the setting where naive bidding is punished. citeturn12view1turn12view0

### Step two: compute your max willingness-to-pay as a _difference in expected outcomes_

For any auctioned card \(c\) at current state \(S\), define:

- \(EV\_{\text{win}}(c \mid S)\): your expected end-of-round chips if you win the card (accounting for improved showdown equity and downstream trading), minus what you pay.
- \(EV\_{\text{lose}}(c \mid S)\): your expected end-of-round chips if you do not win the card (including the possibility an opponent wins it and becomes stronger).

Then your **theoretical max bid** in a sequential-auction sense is:

\[
\text{WTP}(c \mid S) = EV*{\text{win-no-price}}(c \mid S) - EV*{\text{lose}}(c \mid S)
\]

This is exactly the “marginal utility” difference that the sequential-auctions agent literature shows is optimal in the modeled setting. citeturn11view2turn10view2turn5view3

In Sold ’Em terms, WTP naturally decomposes into three parts:

1. **Use value**: how much your showdown equity improves if you own \(c\).
2. **Deny value**: how much your showdown equity worsens if a particular opponent owns \(c\).
3. **Option/resale value**: how much future profitable trading \(c\) enables.

Resale-option effects are not hand-wavy: formal resale models show they change incentives and can alter equilibrium behavior. citeturn5view5

### Step three: translate WTP into an actual bid under your auction implementation

- If bidding is open ascending: your mechanically correct play is to **stay in until price reaches WTP, then stop**, because at any higher price you are no longer buying positive EV. This logic aligns with how ascending auctions can be modeled as “drop out at your threshold” in classic treatments. citeturn6view3turn12view0
- If bidding is sealed/commitment-style: shade below WTP, with shading increasing as the number of plausible competing bidders increases. A simple and widely taught benchmark is \((n-1)/n\) shading in a symmetric uniform model. citeturn6view1

### Step four: as a seller, you are pricing _the harm you cause yourself_

When you auction a card you currently hold, “what it’s worth” is not what it would sell for on average. It is:

\[
\text{MinAccept}(c \mid S) = EV*{\text{keep}}(c \mid S) - EV*{\text{sell}}(c \mid S)
\]

where \(EV\_{\text{sell}}\) must reflect that the buyer gets the card and may beat you. This is the place most players leak EV: they sell a card that is not very valuable _to them_ but is extremely valuable _against them_.

This “sell-side marginal utility” is the mirror image of the buy-side rule, and it is exactly the logic that marginal-utility bidding papers emphasize when they talk about reasoning over sets rather than independent item values. citeturn10view1turn11view2

## Exploiting game-specific edges: house auction and orbit timing

### The house auction is not priced like the others

In your first (house) auction, the paid chips go into the main pot rather than to another player. That changes the “effective cost” of overbidding: when you pay into the pot, you partially “rebate yourself” in expectation proportional to your expected share of the pot at showdown.

So, compared with a normal auction, you should be willing to bid **more** for the same card if (and only if) you believe you will capture a large share of the pot by showdown. In winner-take-all, this is close to “if my win probability is high, paying into the pot is less painful.” If the game mode splits the pot, replace “win probability” with “expected pot share.”

This logic is consistent with the broader auction-theory point that outcomes shift when payoffs depend on the intrinsic qualities and on participants’ preferences and information—and when the mechanism changes the mapping from bids to payoffs. citeturn12view1turn12view0

### Order matters: sell expensive “need cards” early, buy “finishing cards” late

Because budgets are limited and auctions come in a small number of orbits, an opponent’s ability to pay often declines as the round progresses. Sequential-auction evidence and discussion of price trends motivate a simple exploit:

- **Early orbit**: auction cards that more than one opponent plausibly “must have,” encouraging a bidding war while stacks are still deep.
- **Later orbits**: hunt for underpriced cards that complete your hand when opponents are either budget-constrained or already committed elsewhere.

Empirical work documents that declining-price patterns are common in sequential auctions, and theory notes that what is revealed between rounds affects later behavior. citeturn10view3turn5view6turn5view7

### Information discipline: don’t broadcast your plan unless it helps you

Interdependent-values models emphasize that bids can reveal information that changes others’ behavior. citeturn12view0turn12view1  
In Sold ’Em, if you loudly bid up every card of one suit, you invite opponents to:

- tax you by auctioning cards you need,
- block you preemptively,
- infer your maximum pain threshold.

So you generally want a “quiet build” phase unless you are intentionally creating a decoy or you are already so far ahead that information leakage is less costly.

## What to build in the next few hours

You asked specifically for “precompute anything we want” and “design a system.” The best use of prep time is to build a lightweight **equity-and-pricing engine** that outputs WTP/MinAccept quickly.

### Precompute a fast hand evaluator for the Sold ’Em deck

You need two capabilities:

1. Given a set of cards, compute the best five-card hand category (and tie-breakers).
2. Given partial information (your hand + known opponent cards + remaining unknown cards), estimate win probability and expected pot share.

Poker software engineering has a mature toolkit here: evaluators often speed things up by avoiding brute-force enumeration and instead using compact encodings and precomputed tables (e.g., perfect-hash approaches). citeturn13view0  
Even if you don’t reuse that exact code, the design lesson is crucial: **hand evaluation must be fast enough to run thousands of simulations per decision**.

### Build a Monte Carlo equity calculator tailored to your rules

Your simulator should parameterize:

- showdown mode: winner-take-all vs split pots,
- whether five-of-a-kind exists and where it ranks,
- whether players can hold more than five cards and choose best five (as in many community-card variants) citeturn5view9turn14view0,
- presence/number of community cards.

Then, for each auctioned card \(c\), compute:

- your equity if you win \(c\),
- your equity if the most likely opponent to win \(c\) wins it,
- the difference (that’s the deny value),
- the implied WTP.

This is directly aligned with the MDP/marginal-utility framing shown in sequential-auction agent work. citeturn11view2turn10view2turn5view3

### Add a live “price model” layer (simple beats fancy)

The sequential-auction literature emphasizes learning or assuming price distributions as part of computing optimal or near-optimal policies. citeturn5view3turn11view2turn5view6  
For a human-usable tool, you don’t need anything exotic:

- Maintain a rolling estimate of “going price” by hand-improvement type (e.g., “completes flush,” “completes straight,” “third-of-a-kind maker,” “random high card”).
- Update after each auction based on realized clearing prices.
- Use that to forecast how expensive it will be to finish particular lines (flush line, straight line, set-to-full-house line).

### Prepare a small set of “default lines” so you’re never lost

From an EV standpoint, you want flexible plans that don’t require a single exact card.

A useful hierarchy (assuming classic high-hand scoring) is:

- **Robust value line**: build toward **two pair / trips** first (these happen more often and don’t require a single suit to cooperate).
- **Explosive value line**: pursue **flush/straight/straight flush** when you already have strong concentration (e.g., 4 cards in one suit or 4-in-a-row ranks).
- **Punish line**: when an opponent is clearly committed, pivot to selling them the missing piece _only if the price exceeds the equity you lose by strengthening them_ (your MinAccept rule).

This ties back to the core agent insight: value is not per-item; it’s marginal value relative to your current set. citeturn10view1turn11view2

### A final practical note: your biggest edge is being “the only one who prices correctly”

In many real auctions, better information and better valuation translates into higher expected payoff; even the high-level auction theory surveys emphasize that mechanisms, information, and strategic behavior are central to outcomes. citeturn5view1turn12view1turn6view1  
Sold ’Em is designed so that most players will bid emotionally on “cool-looking” cards or chase obvious draws without pricing deny value. If you consistently:

- compute WTP as an equity delta,
- refuse negative-EV hero bids,
- demand correct compensation when selling cards that upgrade opponents,

you should accumulate EV over many rounds.

What are the exact showdown rules in your play environment—do players form the best five-card hand from all cards they hold (plus any community cards), and is five-of-a-kind a recognized hand category?
