# Literature review for auctions, human play, and imperfect-information strategy

Local timestamp: 2026-03-01 03:12:00 PST

## Scope

This note targets Sold 'Em design decisions: first-price private bidding, repeated interaction with humans, imperfect information, and exploit-vs-robust tradeoffs.

## Core auction theory and repeated-auction dynamics

- Milgrom and Weber (1982), "A Theory of Auctions and Competitive Bidding" (Econometrica): canonical interdependent-value auction framework and linkage insights. Source: https://www.econometricsociety.org/publications/econometrica/issue/1982/09/5
- Han, Zhou, Weissman (2020), "Optimal No-regret Learning in Repeated First-price Auctions": first-price learning with censored feedback admits near-optimal regret rates; useful for adaptive bid tuning under partial observability. Source: https://arxiv.org/abs/2003.09795
- Banchio and Skrzypacz (2022), "Artificial Intelligence and Auction Design": repeated first-price formats can drift toward tacitly collusive low bids under simple learners; feedback and mechanism details strongly matter. Source: https://arxiv.org/abs/2202.05947
- Bajari and Yeo (2008), "Auction Design and Tacit Collusion in FCC Spectrum Auctions": reduced bid visibility can suppress signaling/collusion channels. Source: https://www.nber.org/papers/w14441
- Bos et al. (2017), "Collusion and information revelation in auctions": even failed collusion attempts can distort subsequent first-price bidding. Source: https://www.sciencedirect.com/science/article/abs/pii/S0014292117300594
- Hopenhayn and Skrzypacz (2001), "Tacit Collusion in Repeated Auctions": repeated settings support coordination effects even with limited monitoring. Source: https://www.gsb.stanford.edu/faculty-research/working-papers/tacit-collusion-repeated-auctions

## Human behavior and bounded rationality in auctions

- Isaac and Salmon (2013), "Bidding in private-value auctions with uncertain values": overbidding above expected value occurs at meaningful rates in lab settings. Source: https://www.sciencedirect.com/science/article/abs/pii/S0899825613001188
- Gentry et al. (2022), "Robust inference in first-price auctions: Overbidding as an identifying restriction": overbidding is persistent enough to model directly as a structural restriction. Source: https://www.sciencedirect.com/science/article/abs/pii/S0304407622001221
- Cotten, Li, Santore (2021), "Social Preferences and Collusion": social preference and social context shift collusion tendencies in repeated competition. Source: https://www.mohrsiebeck.com/en/article/social-preferences-and-collusion-a-laboratory-experiment-101628jite-2020-0049/

## Imperfect-information game solving and poker AI

- Zinkevich et al. (2007), "Regret Minimization in Games with Incomplete Information": introduces CFR, the dominant large imperfect-information baseline. Source: https://papers.nips.cc/paper/3306-regret-minimization-in-games-with-incomplete-information
- Heinrich and Silver (2016), "Deep Reinforcement Learning from Self-Play in Imperfect-Information Games": NFSP learns approximate equilibria end-to-end without handcrafted abstraction. Source: https://arxiv.org/abs/1603.01121
- Moravcik et al. (2017), "DeepStack": depth-limited continual re-solving plus learned value estimates beats pros in HUNL. Source: https://pubmed.ncbi.nlm.nih.gov/28254783/
- Brown and Sandholm (2018), "Libratus": blueprint + nested subgame solving + self-improvement loop, superhuman in HUNL. Source: https://pubmed.ncbi.nlm.nih.gov/29249696/
- Brown and Sandholm (2019), "Pluribus": superhuman in 6-player multiplayer poker, showing practical mixed-strategy exploitation/robustness in multi-agent settings. Source: https://pubmed.ncbi.nlm.nih.gov/31296650/

## Opponent modeling and exploitation literature

- Southey et al. (2012), "Bayes' Bluff": Bayesian posterior opponent modeling and response selection in poker. Source: https://arxiv.org/abs/1207.1411
- Wu et al. (2021), "L2E: Learning to Exploit Your Opponent": meta-learned exploitation can adapt quickly with few interactions. Source: https://arxiv.org/abs/2102.09381
- Teofilo and Reis (2013), "Identifying Players' Strategies...": clustering player actions into style archetypes can improve predictive play. Source: https://arxiv.org/abs/1301.5943

## Recent additions (2023-2026)

- Jin et al. (2025), "Best of Many Sampled Policies in Learning to Solve Imperfect-Information Games": policy sampling/selection can improve exploitability-quality tradeoffs in large IIGs. Source: https://arxiv.org/abs/2502.11323
- Sellam et al. (2026), "Algorithmic collusion in dynamic auctions with a random number of players": collusive dynamics can emerge under repeated dynamic auction play, reinforcing explicit anti-correlation safeguards in simulations. Source: https://arxiv.org/abs/2601.03853
- Wang et al. (2026), "Deep Opponent Modeling in Repeated Incomplete Information Games": improves adaptation to non-stationary opponents using richer history embeddings. Source: https://arxiv.org/abs/2602.12253

## Implications for Sold 'Em

- Use fair-value anchoring, but avoid purely equilibrium play: empirical overbidding/correlation means exploitative policies can outperform static Nash-like behavior in short horizons.
- Track opponent aggression and pairwise social dynamics explicitly: repeated-game tacit coordination can materially change optimal bid shading.
- Keep a robust fallback policy: exploitative lines are high upside but can be fragile if table composition changes.
- Treat signal quality as sparse and delayed: update player models online from bid streams and showdowns.
- Prefer mixed action sets over deterministic scripts: deterministic behavior becomes exploitable in repeated human games.

## How this informed this codebase

- Added and evaluated exploitative yet risk-aware strategy variants (`market_maker_tight`, `regime_switch_robust`, `regime_switch`, `market_maker_aggr`).
- Promoted champion defaults to `market_maker_tight` (EV/first place) and `regime_switch_robust` (robust fallback).
- Ran long multi-seed validation across horizons and correlation regimes to reduce selection noise.
- Retained multi-objective tournament evaluation with explicit correlation models to capture non-Nash human dynamics.
- Integrated remote PocketBase tracking to preserve strategy metadata and experiment outputs for iterative bootstrapping.
