# Literature review for auction strategy and imperfect-information play

Local timestamp: 2026-03-01 01:24 PST

This note focuses on literature directly useful for Sold 'Em: first-price auction behavior, bounded-rational opponent models, and practical imperfect-information game-solving methods.

## Core auction behavior findings

### Winner’s curse and overbidding are persistent in common-value settings

- Kagel and Levin (1986) shows systematic winner’s curse effects in common-value first-price auctions, especially with more bidders and early/less-adapted play: https://econpapers.repec.org/RePEc:aea:aecrev:v:76:y:1986:i:5:p:894-920
- Lind and Plott (1991) replicates and extends winner’s curse behavior in lab settings: https://authors.library.caltech.edu/records/b87sp-73n31

Implication for Sold 'Em:

- In house auctions and high-uncertainty card spots, opponents can overpay relative to conditional value.
- Strategy search should include exploiter policies that intentionally list tempting but noisy-value cards to induce overbids.

### Non-equilibrium strategic thinking explains auction mispricing

- Crawford and Iriberri (2007) level-k auctions: nonequilibrium belief hierarchy helps explain both winner’s curse and private-value overbidding: https://econpapers.repec.org/RePEc:ecm:emetrp:v:75:y:2007:i:6:p:1721-1770
- Camerer, Ho, Chong (2004) cognitive hierarchy model (bounded iterated reasoning): https://academic.oup.com/qje/article-abstract/119/3/861/1938841
- Crawford, Costa-Gomes, Iriberri (2013) structural survey of nonequilibrium strategic thinking: https://ideas.repec.org/a/aea/jeclit/v51y2013i1p5-62.html

Implication for Sold 'Em:

- Opponent pools should not be approximated as one equilibrium type.
- Population training should include level-0/1/2 style bidders and adaptive profile estimates during live play.

### Learning dynamics matter more than static equilibrium in repeated human play

- Erev and Roth (1998) reinforcement learning models often predict repeated-play behavior better than static mixed-strategy equilibrium in long-horizon experiments: https://econpapers.repec.org/RePEc:aea:aecrev:v:88:y:1998:i:4:p:848-81

Implication for Sold 'Em:

- Day-of strategy should update opponent profiles round by round.
- Advisor should track observed bid aggression and shift price recommendations online.

## Imperfect-information game solving findings

### CFR and MCCFR remain foundational for tractable imperfect-information solving

- Zinkevich et al. (2007), CFR in extensive-form games: https://papers.nips.cc/paper/3306-regret-minimization-in-games-with-incomplete-information
- Lanctot et al. (2009), MCCFR sampling variants with convergence guarantees: https://papers.nips.cc/paper/3713-monte-carlo-sampling-for-regret-minimization-in-extensive-games

Implication for Sold 'Em:

- Full-tree exact methods are unnecessary for rapid overnight research.
- Sampled simulation with compact state abstractions is the practical baseline.

### Real-world poker AIs combine equilibrium backbones with practical local adaptation

- DeepStack (Science 2017; project/supplement links):
  - PubMed: https://pubmed.ncbi.nlm.nih.gov/28254783/
  - Project page: https://www.deepstack.ai/
- Brown and Sandholm (2017), safe and nested subgame solving: https://papers.nips.cc/paper/6671-safe-and-nested-subgame-solving-for-imperfect-information-games
- Pluribus (Science 2019), multiplayer poker superhuman play:
  - PubMed: https://pubmed.ncbi.nlm.nih.gov/31296650/

Implication for Sold 'Em:

- Hybrid approach is best: stable baseline policy + local re-evaluation at decision time.
- For multiplayer settings, exploitability and practical robustness trade off; pure Nash approximation is not sufficient.

### Deep self-play alternatives are viable but engineering-heavy

- Heinrich and Silver (2016), NFSP in imperfect-information games: https://arxiv.org/abs/1603.01121
- Farina, Kroer, Sandholm (2020), stochastic regret minimization improvements: https://arxiv.org/abs/2002.08493
- Schmid et al. (2018), variance-reduced MCCFR: https://arxiv.org/abs/1809.03057

Implication for Sold 'Em:

- Useful for future extensions, but for sub-6-hour delivery deterministic simulation + policy search gives better implementation-risk profile.

## Directly adopted in this codebase

- Multi-policy population search with objective toggles (`ev`, `first_place`, `robustness`).
- Correlated-opponent modes (`respect`, `herd`, `kingmaker`) to model social dynamics.
- Champion selection by both single objectives and configurable composite profiles.
- Live session profiling (aggression, average bids) for in-game adaptation.

## Open research gaps for next iteration

- Explicit collusion/coalition signaling models in 5-player first-price card auctions.
- Better calibration of bid win-probability model using real human logs from practice games.
- Robust optimization against adversarial policy mixtures, not only random seat-map sampling.
