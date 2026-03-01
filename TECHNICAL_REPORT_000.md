# Technical report 000

Local timestamp: 2026-03-01 07:35 PST

## Abstract

This report is a mathematical briefing for a reader who knows only the Sold 'Em rules. It explains what we learned overnight about strategy, why those conclusions follow from the data, and where uncertainty remains.

The short answer is that the game has no single universally best policy under all reward definitions. The dominant policy depends on what you optimize:

- maximizing expected chip profit (`ev`)
- maximizing probability of finishing first (`first_place`)
- maximizing tail-protected performance (`robustness`)

Across our largest baseline sweeps, conservative policies were surprisingly stable for EV and often for first-place in human-like pools, while level-k style adaptive policies took many robustness and correlation-stress regimes. Independent parallel tracks also discovered materially different optima (market-maker/regime-switch and seller-extraction families), which indicates a genuinely multimodal policy landscape rather than one clear global champion.

## Game model from rules

Under the stated rules, each round creates two linked markets:

1. a sequence of first-price private auctions for cards
2. a terminal hand-resolution payout from the round pot

Each player enters with fixed chips each round (stack resets), pays ante, trades via auctions, then realizes showdown payout according to the active payout variant. Total tournament standing is accumulated PnL across rounds.

At a high level, round PnL for player $i$ can be viewed as:

$$
\text{PnL}_i
=
\text{showdown\_payout}_i
- \text{ante}
- \text{auction\_spend}_i
+ \text{auction\_sales\_income}_i
$$
  code
with an additional coupling through the first house auction (spend goes to pot, not to another player), which changes both price formation and future auction order.

This structure creates a classical multi-agent tradeoff:

- bid too low: lose high-value card opportunities and downstream showdown equity
- bid too high: overpay (winner's curse behavior), reducing net PnL even if hand quality improves
- sell too aggressively: gain immediate chips but potentially leak long-run showdown equity

## Statistical objective definitions

We evaluated policies under three explicit objectives:

- `ev`: $ \mathbb{E}[X] $, where $X$ is per-game PnL
- `first_place`: $ \Pr(R=1) $, where $R$ is finishing rank
- `robustness`: $ \mathbb{E}[X] - \max(0,-\text{CVaR}_{20\%}(X)) $

Interpretation of robustness:

- downside tails are explicitly penalized
- upside variance is not directly penalized
- a moderate-EV, stable policy can beat a higher-EV but crash-prone policy

This objective split matters because first-place and EV are not aligned in this game.

## Experimental protocol used overnight

We ran replicated Monte Carlo tournaments over policy sets, then selected winners by either mean estimate or a conservative lower-confidence bound (LCB).

Condition keys were formed by:

$$
(\text{rule profile},\ \text{objective},\ \text{horizon},\ \text{correlation mode})
$$

Main scenario axes:

- horizon $H \in \{3,5,7,10,20,30\}$
- correlation mode $C \in \{\text{none}, \text{respect}, \text{herd}, \text{kingmaker}\}$
- multiple rule profiles (baseline plus built-in variants)
- opponent populations:
  - symmetric round-robin pools
  - weighted human-like pools

Correlation was injected via paired-player behavioral transforms:

- `respect`: paired players shade bids against each other
- `herd`: paired players partially follow partner bid direction
- `kingmaker`: paired players suppress bids on partner selling turns

We tracked winner counts, margins, SEM-based 95% confidence intervals, and LCB winners.

## Overnight narrative and findings

## Phase 1: broad baseline stress established a stable anchor

In the broad h10 stress run (`long_parallel_matrix_20260301_020705.analysis.md`), we evaluated many strategies across profiles and correlation modes.

Aggregate result:

- mean winner counts: `conservative=31`, `meta_switch=9`, `meta_switch_soft=8`
- LCB winner counts: `conservative=31`, `meta_switch_soft=10`, `meta_switch=7`

This is unusually concentrated for a 5-player imperfect-information setting: one family (`conservative`) won roughly two-thirds of condition cells even after conservative confidence adjustment.

Mathematical interpretation:

- in many cells, avoiding auction overpayment dominated speculative upside
- house-auction coupling and repeated first-price dynamics amplify overbidding penalties

## Phase 2: horizon sweeps showed strong nonstationarity

In `long_parallel_matrix_20260301_033913.analysis.md` (horizons 3/7/10/20/30), tuned level-k variants dominated many EV and robustness cells.

Winner-count summary:

- mean: `levelk_base=13`, `levelk_926417=12`, `levelk_207605=8`, `level_k=8`, others smaller
- LCB: still concentrated in tuned level-k variants and `level_k`

Interpretation:

- strategy quality is horizon-dependent
- short-horizon winners do not automatically transfer to longer horizons

## Phase 3: correlation-strength sweeps changed the ranking order

In `correlation_sweep_20260301_025118.md`, increasing correlation strength shifted winners heavily toward tuned level-k forms.

Winner counts in that sweep:

- `level_k_l3: 34`
- `levelk_207605: 33`
- `level_k: 21`
- `meta_switch: 11`
- `meta_switch_soft: 7`
- `conservative: 2`

Interpretation:

- once social coupling is introduced, adaptive reasoning-depth models gain relative value
- correlation is first-order: it can invert policy rankings

## Phase 4: first-place objective exposed a structural conflict

Independent finalist analyses and several matrices repeated the same pattern:

- policies with high first-place rate can have materially lower EV
- in one finalist set, `pot_fraction` won first-place in `12/12` cells, yet had negative EV in many of those environments

So the optimization surface is truly multi-objective, not noisy estimates of the same optimum.

## Phase 5: human-like pool simulations corrected some early impressions

In the largest hero-vs-weighted-human pool run (`hero_pool_matrix_20260301_054854.md`, 1188 rows), winners were mixed:

- conservative: 12
- level_k: 12
- meta_switch_soft: 6
- level_k_l3: 4
- others: small counts

Then focused high-sample validation reduced uncertainty:

- `hero_pool_matrix_20260301_061711.md`:
  - baseline h10 `first_place`: `conservative` won all 4 correlation modes
  - baseline h10 `robustness`: `level_k` won all 4 modes
- `hero_pool_matrix_20260301_065716.md`:
  - standard-rankings h10 `first_place`: `conservative` won all 4 modes, including kingmaker

Interpretation:

- human-like weighting made first-place recommendations more conservative than some symmetric-population runs suggested
- this materially changed the final pre-7am prior

## Final policy prior extracted from overnight evidence

From the final condition map (`dayof_policy_hybrid_v11_lcb.json`):

- global defaults:
  - `ev`: `meta_switch_soft`
  - `first_place`: `conservative`
  - `robustness`: `level_k`
- condition count: `180`

Winner mass across those 180 conditions:

- EV: mostly `conservative` and `meta_switch_soft`, then `level_k` variants
- first-place: heavily `conservative`
- robustness: split across `conservative`, `meta_switch`, and `level_k`

This is the data-driven prior from the overnight run stack.

## Independent parallel discoveries (important for interpretation)

Three other overnight tracks found different local optima:

1. market-maker/regime-switch track (`v3`)
   - EV finalist winner `mm_r0090`: `12/12` cells
   - robustness finalist winner `rs_v2`: `12/12`
   - tournament-win long winner `market_maker_v2`: `4/4`

2. dynamic routing track (`v4`)
   - first-place routing calibration fit: `68/80 = 0.85` hit rate on target winner mapping
   - emphasized variant-aware rule switching and correlated-pair defenses

3. distributed seller-extraction track (`v5`)
   - merged distributed validation over `864` scenarios
   - promoted champions:
     - EV: `seller_extraction(opportunistic_delta=5400,reserve_bid_floor=0.032,sell_count=2)`
     - first_place: `seller_profit`
     - robustness: `seller_extraction(opportunistic_delta=4500,reserve_bid_floor=0.02,sell_count=2)`

Why this matters mathematically:

- the response surface has multiple competitive basins
- different objective formulations and evaluation protocols can select different policy families

## What this implies for a mathematically informed operator

The main lesson is conditional policy selection:

$$
\pi^* = \pi^*(\text{objective},\ \text{horizon},\ \text{correlation regime},\ \text{rule profile})
$$

not

$$
\pi^* = \text{single fixed policy}
$$
  
Concretely from overnight data:

- for EV with no strong abnormal social signal, `meta_switch_soft` is a robust prior
- for first-place in realistic human pools, `conservative` is safer than earlier high-variance alternatives
- for robustness and correlated-table contingencies, level-k variants remain important challengers

## Remaining uncertainty

Two uncertainties are still first-order:

1. Cross-family apples-to-apples integration:
   - market-maker and seller-extraction families were not fully benchmarked in one unified harness with identical objective accounting and condition-map logic.

2. Regime detection error:
   - gains from correlation-aware switching depend on correctly identifying whether live table behavior is closer to `none`, `respect`, `herd`, or `kingmaker`.

## Recommended next mathematical step

Run one unified head-to-head matrix with identical definitions for:

- current finalists (`conservative`, `meta_switch_soft`, tuned `level_k` variants)
- market-maker/regime-switch finalists
- seller-extraction finalists

with the same:

- rule profiles
- horizons
- correlation modes
- human-like opponent pool
- LCB selection criterion

Promote replacements only where both mean and LCB improve.

## Bottom line

Overnight evidence supports an objective-aware, horizon-aware, correlation-aware strategy framework. The strongest stable finding is not that one policy dominates globally; it is that objective and regime jointly determine the optimum. Conservative play remains a strong anchor, while adaptive families are essential in specific regimes.
