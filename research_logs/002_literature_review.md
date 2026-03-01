# Literature review for Sold 'Em strategy design

Local time: 2026-03-01 01:56 PST

## Scope

This note focuses on directly actionable findings for first-price sealed bidding, imperfect-information game solving, and human strategic behavior under repeated play.

## Key findings and implications

1. Auction format and information release strongly affect bidding levels and seller revenue.
Inference for Sold 'Em: house-auction and seller turns should be modeled separately from buy EV, because information and sequencing change behavior.
Source: Milgrom and Weber (1982), "A Theory of Auctions and Competitive Bidding" ([Kellogg summary](https://www.kellogg.northwestern.edu/academics-research/research/detail/1982/a-theory-of-auctions-and-competitive-bidding/)).

2. In fixed-deadline auctions, strategic late action is rational, not just noise.
Inference for Sold 'Em: in 10-second private bids, expect late/hidden aggression and mixed tactics; deterministic patterns are exploitable.
Sources: Roth and Ockenfels (2000 working paper, 2002 AER publication) ([NBER w7729](https://www.nber.org/papers/w7729), [AER 2002](https://www.aeaweb.org/articles?id=10.1257/00028280260344632)).

3. Overconfidence increases entry and aggressive participation.
Inference for Sold 'Em: include human archetypes that over-bid high-upside spots and under-price downside tail risk.
Source: Camerer and Lovallo (1999), "Overconfidence and Excess Entry" ([AER](https://www.aeaweb.org/articles?id=10.1257/aer.89.1.306)).

4. Common-value style settings produce winner's curse dynamics; participation and outside options matter.
Inference for Sold 'Em: when auction value is mostly from future table effects (not just immediate hand gain), apply bid shading and scenario-based reserve thresholds.
Source: Cox, Dinkin, and Swarthout (2001), "Endogenous Entry and Exit in Common Value Auctions" ([Cambridge](https://www.cambridge.org/core/journals/experimental-economics/article/endogenous-entry-and-exit-in-common-value-auctions/DC4664D64F75A6BA27DBB79C5C48295C)).

5. Counterfactual regret minimization and descendants are strong foundations for imperfect-information strategy quality.
Inference for Sold 'Em: policy populations and response-based search are more reliable than single fixed heuristics.
Sources: Zinkevich et al. (2007) CFR ([NeurIPS](https://papers.nips.cc/paper_files/paper/2007/hash/08d98638c6fcd194a4b1e6992063e944-Abstract.html)); Bowling et al. (2015) CFR+ at scale ([PubMed](https://pubmed.ncbi.nlm.nih.gov/25574016/)).

6. Real-time subgame solving and self-improvement beat static equilibrium approximations in poker-like domains.
Inference for Sold 'Em: keep a robust default strategy, but maintain fast adaptive fallback modes for correlated or adversarial tables.
Sources: DeepStack (2017) ([PubMed](https://pubmed.ncbi.nlm.nih.gov/28254783/)), Libratus (2018) ([PubMed](https://pubmed.ncbi.nlm.nih.gov/29249696/)), Pluribus (2019) ([PubMed](https://pubmed.ncbi.nlm.nih.gov/31296650/)).

7. Population-based game-theoretic learning reduces overfitting to a single opponent style.
Inference for Sold 'Em: maintain strategy pools and periodic cross-play refresh (hero-vs-pool + correlated scenarios) to avoid staleness.
Source: Lanctot et al. (2017), "A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning" ([arXiv](https://arxiv.org/abs/1711.00832)).

8. Repeated first-price auctions with censored feedback still admit near-optimal no-regret learning.
Inference for Sold 'Em: repeated-round adaptation from observed winning bids is theoretically well-grounded; use this for day-of profile updates.
Source: Han, Zhou, and Weissman (2020), "Optimal No-regret Learning in Repeated First-price Auctions" ([arXiv](https://arxiv.org/abs/2003.09795)).

## Translation to implementation

1. Use robust baseline + explicit mode switching.
Implemented as `conservative_plus` (default) and `equity_sniper_ultra` (correlation/first-place mode).

2. Simulate non-equilibrium humans, not only equilibrium bots.
Implemented with correlated-opponent models (`respect`, `herd`, `kingmaker`) and mixed-opponent hero benchmarks.

3. Keep exploitability pressure in loop.
Implemented with population tournaments, hero-vs-pool benchmarking, and rule-profile sweeps.

4. Keep strategy registry externalized.
Implemented with PocketBase collections for `strategies`, `eval_runs`, `champions`, `workers`.

## Research gaps to explore next

1. Add explicit coalition/reciprocity models beyond pairwise correlation.
2. Add bidder-level Bayesian updates for inferred private card-value models.
3. Add latency-aware LLM policy fallback constrained to under 10 seconds.
4. Add direct human-in-the-loop training protocol from showdown observations.
