# Sold 'Em literature review

Local timestamp: 2026-03-01 01:40:32 PST

## Scope and objective

This review focuses on literature that is directly useful for Sold 'Em:

- First-price auction theory and bidder behavior.
- Imperfect-information game solving and multiplayer poker.
- Opponent modeling and safe exploitation against non-equilibrium humans.
- Population training methods for non-transitive strategy ecosystems.

The goal is not a full survey. The goal is to extract practical design rules for strategy search and day-of play.

## What the literature says and why it matters here

### Auction game theory foundations

- Vickrey (1961) is the canonical base for sealed-bid auction analysis and strategic bid shading.
- Milgrom and Weber (1982) formalize auctions with interdependent/common values and show information structure and auction format strongly affect outcomes and revenue.
- Practical implication for Sold 'Em:
- A naive "bid true value" strategy is generally dominated in first-price environments.
- Information release and observability affect collusion/tacit coordination risk.

### Human behavior in auctions is not fully rational

- Winner's-curse experiments show systematic overbidding in common-value settings, especially early and among less experienced participants.
- Lind and Plott (1991) replicate and extend winner's-curse effects in controlled experiments.
- Practical implication for Sold 'Em:
- Against humans, exploitative reserve-selling and selective buying can outperform equilibrium-style "fair" bidding.
- Early-game overbidding pressure from humans is likely and should be harvested.

### Imperfect-information poker progress

- CFR introduced counterfactual regret minimization as a scalable path to approximate equilibrium in large imperfect-information games.
- MCCFR reduces per-iteration cost with sampling while preserving convergence behavior in expectation.
- Libratus (2018) and Pluribus (2019) show strong game-theoretic planning plus online adaptation can beat top pros.
- Depth-limited solving work highlights robustness by evaluating multiple continuation strategies, not one brittle continuation value.
- Practical implication for Sold 'Em:
- Build strong baseline strategies using regret/response ideas, then adapt online to observed humans.
- Robustness to multiple opponent responses is more important than point-optimal tuning.

### Opponent modeling and multiplayer adaptation

- Bayes' Bluff and later Bayesian exploitation papers show posterior-based opponent response can outperform static play.
- Recent multiplayer imperfect-information work (Ganzfried et al.) shows observation-driven opponent modeling can beat exact Nash strategies in repeated multiplayer settings.
- Safe exploitation literature formalizes the tradeoff: exploit observed weaknesses while preserving a lower-bound safety guarantee.
- Practical implication for Sold 'Em:
- Maintain per-seat profiles and update bid/aggression priors each auction.
- Use bounded exploitation (caps/floors) instead of unconstrained overfitting.

### Population methods for non-transitive games

- PSRO-style frameworks reduce overfitting to a single opponent by iteratively adding best responses and solving meta-strategies over a policy population.
- Joint-policy correlation (JPC) in MARL highlights overfitting risk when training/evaluating in narrow pools.
- Practical implication for Sold 'Em:
- Keep a diverse strategy pool and continuous round-robin/evolution.
- Include collusion-like correlation models during evaluation to avoid brittle champions.

## Direct strategy implications for Sold 'Em

### Bidding policy

- Treat bid as a first-price control variable, not "price revelation."
- Estimate marginal win value of auction card, then shade by risk, stack constraints, objective, and expected opponent aggression.
- Keep hard caps for robustness. Overpaying in first-price auctions is a consistent failure mode.

### Selling policy

- In human pools, selling for profit is a primary edge.
- Optimize sale bundles by balancing card marketability against hand-damage cost.
- Favor extraction when table exhibits aggressive/competitive bidding.

### Multiplayer exploitability control

- Avoid single-policy lock-in.
- Evaluate every candidate under multiple correlation dynamics (none, respect pairs, herd behavior, kingmaker patterns).
- Prefer strategies that remain top-ranked across objective profiles and rule variants.

### Online adaptation

- Update player profiles each auction:
- mean bid
- aggression proxy (bid/start_stack)
- observed tie timing behavior
- After showdown, update inferred card preferences and role tendencies for subsequent rounds.

## Implementation guidance derived from literature

### Recommended training loop

- Maintain a strategy database with metadata: family, params, known weaknesses, objective performance.
- Run evolutionary or PSRO-lite cycles:
- evaluate candidate vs pool
- keep top robust performers
- generate mutated/exploitative responses
- re-evaluate old strategies periodically to avoid staleness
- Score by multi-objective composite:
- EV
- first-place rate
- downside robustness (tail-aware)
- objective-conditioned leaderboards

### Recommended day-of mode

- Use robust champion as default.
- Allow fast objective switch (`ev`, `first_place`, `robustness`).
- Keep top 2-3 fallback strategies precomputed for rule/profile changes.

## Key references

- Zinkevich et al., 2007, Regret Minimization in Games with Incomplete Information (NeurIPS). https://papers.nips.cc/paper/3306-regret-minimization-in-games-with-incomplete-information
- Lanctot et al., 2009, MCCFR (NeurIPS). https://papers.nips.cc/paper/3713-monte-carlo-sampling-for-regret-minimization-in-extensive-games
- Tammelin, 2014, CFR+. https://arxiv.org/abs/1407.5042
- Heinrich and Silver, 2016, NFSP. https://arxiv.org/abs/1603.01121
- Brown et al., 2018, Deep CFR. https://arxiv.org/abs/1811.00164
- Brown and Sandholm, 2018, Libratus (Science/PubMed). https://pubmed.ncbi.nlm.nih.gov/29249696/
- Brown and Sandholm, 2019, Pluribus (Science/PubMed). https://pubmed.ncbi.nlm.nih.gov/31296650/
- Brown, Sandholm, Amos, 2018, Depth-limited solving. https://arxiv.org/abs/1805.08195
- Lanctot et al., 2017, unified game-theoretic MARL / PSRO roots. https://arxiv.org/abs/1711.00832
- Lanctot et al., 2019/2020, OpenSpiel framework. https://arxiv.org/abs/1908.09453
- Southey et al., Bayes' Bluff (UAI). https://arxiv.org/abs/1207.1411
- Ganzfried et al., 2022/2024, Opponent modeling in multiplayer imperfect-information games. https://arxiv.org/abs/2212.06027
- Jeary and Turrini, 2023, safe opponent exploitation for epsilon-equilibrium strategies. https://arxiv.org/abs/2307.12338
- Vickrey, 1961, Counterspeculation, Auctions, and Competitive Sealed Tenders. https://jmvidal.cse.sc.edu/lib/vickrey61a.html
- Milgrom and Weber, 1982, A theory of auctions and competitive bidding (bibliographic entry and PDF listing). https://www.scholars.northwestern.edu/en/publications/a-theory-of-auctions-and-competitive-bidding and https://web.stanford.edu/~milgrom/publishedarticles/
- Lind and Plott, 1991, The winner's curse experiments. https://authors.library.caltech.edu/records/b87sp-73n31
- Bajari and Yeo, 2008/2009, auction design and tacit collusion. https://www.nber.org/papers/w14441
- Kumar et al., 2024, strategically-robust learning in repeated first-price auctions. https://arxiv.org/abs/2402.07363
