# 7am handoff summary

Local timestamp: 2026-03-01 07:00:00 PST

## Final champion policy

- `ev`: `market_maker_v2`
- `first_place` (safe default): `market_maker_v2`
- `robustness`: `regime_switch_v2`
- `tournament_win`: `market_maker_v2`

High-variance override:

- `first_place` pure win-rate mode: `pot_fraction` (sacrifices EV).

## Why this is final

This configuration is the result of layered validation:

1. Large baseline/candidate sweeps.
2. Multi-seed long matrices across horizons/correlation modes.
3. Rule-profile matrix across all built-in variant profiles.
4. Extreme-correlation stress tests.
5. Finalist re-search around tuned reserve and regime parameters.

In the finalist long runs (`finalists_long_*.json`):

- `mm_r0090` (now exposed as `market_maker_v2`) won EV in all cells (`12/12`).
- `rs_v2` (now `regime_switch_v2`) won robustness in all cells (`12/12`).
- `pot_fraction` won first-place-rate cells but with large negative EV.
- Tournament-win fast and long matrices selected `market_maker_v2` in all correlation cells (`4/4` in each run).
- Tournament-win horizon matrix (`5,10,20`) selected `market_maker_v2` in `9/12` cells (remaining `3/12` were `market_maker_tight`).
- Tournament-win profile fast pass briefly favored `market_maker_tight` for `standard_rankings` and `top2_split`, but higher-confidence tie-break runs flipped both back to `market_maker_v2`.

## Key artifacts

- Finalist long validation:
  - `research_logs/experiment_outputs/finalists_long_ev.json`
  - `research_logs/experiment_outputs/finalists_long_first_place.json`
  - `research_logs/experiment_outputs/finalists_long_robustness.json`
  - `research_logs/experiment_outputs/finalists_tournament_win_fast.json`
  - `research_logs/experiment_outputs/finalists_long_tournament_win.json`
  - `research_logs/experiment_outputs/tournament_win_horizon_fastlong.json`
  - `research_logs/experiment_outputs/rule_profile_tournament_win_fastlong.json`
  - `research_logs/experiment_outputs/rule_profile_tournament_win_tiebreak.json`
- Rule-profile validation:
  - `research_logs/experiment_outputs/rule_profile_validation_long.json`
- Direct EV tie-break:
  - `research_logs/experiment_outputs/mmv2_vs_tight_h2h.json`
- Correlation stress:
  - `research_logs/experiment_outputs/correlation_stress_matrix.json`
  - `research_logs/experiment_outputs/correlation_stress_summary.json`
- Champion docs:
  - `docs/champion_results.md`
  - `docs/day_of_runbook.md`
  - `docs/day_of_patch_guide.md`

## Run now

### Backend

```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

### HUD

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

### Verify

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/session/state
```

## PocketBase status

- Active instance: `i-08f41ea7a4d11aaca`
- URL: `http://44.221.42.217:8090`
- Current records include long validation + stress batches.

## Required reference for future rollouts

During compaction/handoff, include `research_logs/000_god_prompt.md` in required context.
