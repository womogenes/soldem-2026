# Sold 'Em research log

Local timestamp: 2026-03-01 01:45:00 PST

## 01:28 PST
- Audited `RULES.md`, engine flow, ranking utilities, strategy loader, simulator, API, and HUD.
- Confirmed existing plugin strategy format (`load_strategy`) and compact JSONL game logging.
- Verified baseline unit tests pass with `uv run python -m unittest discover -s tests -q`.

## 01:44 PST
- Ran baseline population sweeps across objectives and correlation modes (`research_logs/experiment_outputs/baseline_*.json`).
- Verified 50-card hand combinatorics exactly (`2,118,760` combinations), confirming `CATEGORY_RARITY_COUNTS_50` and rarity ordering implementation.
- Added strategy families in `strategies/builtin.py`: `market_maker`, `conservative_ultra`, `elastic_conservative`, `conservative_plus`, `mc_edge`.
- Ran candidate sweeps (`research_logs/experiment_outputs/candidates_*.json`): `market_maker` won EV in all 12 objective/correlation runs.
- Ran horizon/correlation matrix (`research_logs/experiment_outputs/horizon_correlation_matrix.json`): `market_maker` won 25/27 cells; `conservative_ultra` won 2 robustness-heavy cells.
- Ran rule-variant matrix (`research_logs/experiment_outputs/rule_variant_matrix.json`): `market_maker` won 14/18 profile/objective cells; robustness fallback usually `conservative_ultra`.
- Updated API default champions in `game/api.py` to `market_maker` (`ev`, `first_place`) and `conservative_ultra` (`robustness`).
- Provisioned PocketBase on AWS EC2 (`i-08f41ea7a4d11aaca`, `44.221.42.217`) and created superuser.
- Added PocketBase automation scripts: `scripts/pocketbase_bootstrap.py`, `scripts/sync_experiments_to_pocketbase.py`.
- Synced candidate experiment outputs to PocketBase and verified records in `strategies`, `eval_runs`, `champions`, and `match_results`.
- Added day-of operations docs in `docs/` and literature review in `research_logs/literature_auction_poker_imperfect_info_2026-03-01.md`.


## 01:47 PST
- Added `scripts/apply_rule_patch.py` and `scripts/precompute_variants.py` for fast day-of operations.
- Added docs in `docs/`: `rule_assumptions.md`, `strategy_format.md`, `cloud_setup.md`, `day_of_runbook.md`, `day_of_patch_guide.md`, `champion_results.md`.
- Added minimal external strategy template at `strategies/examples/minimal_strategy.py`.
- Validated web checks with `pnpm --dir web check` and `pnpm --dir web build`.
- Performed API E2E smoke checks on `/health`, `/session/state`, and `/advisor/recommend`; default strategy resolves to `market_maker`.
- Extended tests in `tests/test_sim_runner.py` for new strategy tags and match smoke.
- Terminated redundant EC2 instance `i-0c4e23958644122b7` to reduce spend.

## 01:46 PST
- Added  and research_logs/variant_precompute/variant_leaderboards.json for fast day-of operations.
- Added docs set in : , , , , , .
- Added minimal external strategy template at .
- Added and validated web checks: 
> web@0.0.1 check /home/willi/coding/trading/soldem-2026/v3/web
> svelte-kit sync && svelte-check --tsconfig ./tsconfig.json

Loading svelte-check in workspace: /home/willi/coding/trading/soldem-2026/v3/web
Getting Svelte diagnostics...

svelte-check found 0 errors and 0 warnings and 
> web@0.0.1 build /home/willi/coding/trading/soldem-2026/v3/web
> vite build

vite v7.3.1 building ssr environment for production...
transforming...
✓ 206 modules transformed.
rendering chunks...
vite v7.3.1 building client environment for production...
transforming...
✓ 159 modules transformed.
rendering chunks...
computing gzip size...
.svelte-kit/output/client/_app/version.json                        0.03 kB │ gzip:  0.05 kB
.svelte-kit/output/client/.vite/manifest.json                      3.69 kB │ gzip:  0.73 kB
.svelte-kit/output/client/_app/immutable/assets/0.CHSELf_x.css    18.67 kB │ gzip:  4.22 kB
.svelte-kit/output/client/_app/immutable/entry/start.sQDd6x1c.js   0.08 kB │ gzip:  0.09 kB
.svelte-kit/output/client/_app/immutable/chunks/CGXeD2LZ.js        0.32 kB │ gzip:  0.25 kB
.svelte-kit/output/client/_app/immutable/chunks/DaODjvW2.js        0.53 kB │ gzip:  0.33 kB
.svelte-kit/output/client/_app/immutable/nodes/1.BlNqa8oX.js       0.55 kB │ gzip:  0.35 kB
.svelte-kit/output/client/_app/immutable/chunks/zqy3SHKI.js        1.49 kB │ gzip:  0.66 kB
.svelte-kit/output/client/_app/immutable/chunks/BrUjG50s.js        2.07 kB │ gzip:  1.09 kB
.svelte-kit/output/client/_app/immutable/nodes/0.QqwYmmh9.js       2.83 kB │ gzip:  1.26 kB
.svelte-kit/output/client/_app/immutable/chunks/CmGNoYqz.js        3.33 kB │ gzip:  1.70 kB
.svelte-kit/output/client/_app/immutable/chunks/C1rIeRTS.js        5.11 kB │ gzip:  2.31 kB
.svelte-kit/output/client/_app/immutable/entry/app.COYpmxbn.js     5.69 kB │ gzip:  2.66 kB
.svelte-kit/output/client/_app/immutable/chunks/JBpPRgiq.js        7.15 kB │ gzip:  3.33 kB
.svelte-kit/output/client/_app/immutable/chunks/ZTmkiM--.js       23.16 kB │ gzip:  9.12 kB
.svelte-kit/output/client/_app/immutable/chunks/Yq8DHcT9.js       26.10 kB │ gzip: 10.27 kB
.svelte-kit/output/client/_app/immutable/nodes/2.vBuMcW0_.js      51.14 kB │ gzip: 17.48 kB
✓ built in 564ms
.svelte-kit/output/server/.vite/manifest.json                           3.70 kB
.svelte-kit/output/server/_app/immutable/assets/_layout.CHSELf_x.css   18.67 kB
.svelte-kit/output/server/chunks/false.js                               0.05 kB
.svelte-kit/output/server/internal.js                                   0.35 kB
.svelte-kit/output/server/chunks/environment.js                         0.62 kB
.svelte-kit/output/server/chunks/utils.js                               1.15 kB
.svelte-kit/output/server/entries/fallbacks/error.svelte.js             1.35 kB
.svelte-kit/output/server/entries/pages/_layout.svelte.js               2.58 kB
.svelte-kit/output/server/chunks/utils2.js                              3.14 kB
.svelte-kit/output/server/chunks/internal.js                            3.17 kB
.svelte-kit/output/server/chunks/exports.js                             7.03 kB
.svelte-kit/output/server/entries/pages/_page.svelte.js                17.96 kB
.svelte-kit/output/server/remote-entry.js                              19.01 kB
.svelte-kit/output/server/chunks/shared.js                             42.65 kB
.svelte-kit/output/server/chunks/index.js                              48.50 kB
.svelte-kit/output/server/chunks/root.js                               78.15 kB
.svelte-kit/output/server/index.js                                    132.87 kB
✓ built in 1.72s

Run npm run preview to preview your production build locally.

> Using @sveltejs/adapter-auto
  Could not detect a supported production environment. See https://svelte.dev/docs/kit/adapters to learn how to configure your app to run on the platform of your choosing
  ✔ done.
- Performed API E2E smoke check (, , ) with default champion resolving to .
- Extended tests to cover new strategy tags and new-strategy match smoke in .
- Terminated redundant EC2 instance  to reduce spend.
