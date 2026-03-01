# Pre-7 summary

Local time: 2026-03-01 06:59:20 PST

## What is ready

1. Live advisor stack is complete:
- Backend API: `game/api.py`
- Web HUD: `web/src/routes/+page.svelte`
- Rule patching: `scripts/day_of_patch.py`
- One-command autosolve + patch: `scripts/day_of_autosolve_patch.py`
- HUD is now `n_players`-aware (dynamic stack slots and seat bounds for non-5-player variants).

2. First-place routing is recalibrated for winner-takes-all variants:
- exact baseline: `meta_switch`
- sprint WTA: `pot_fraction`
- WTA pot-pressure (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)): `pot_fraction`
- WTA high-stack low-ante (`n_orbits>=3`, `start>=180`, `ante/start<0.20`): `equity_evolved_v1`
- remaining non-sprint WTA: `meta_switch`
- non-WTA: `equity_evolved_v1`
- passive high-confidence table read override: `pot_fraction`
- correlated-pair high-confidence table read override: `equity_evolved_v1`

3. Supporting evidence is logged:
- Matrix/horizon runs: `research_logs/experiment_outputs/first_place_rollout_matrix_6c_3h_60m_seed63201.json`
- Hero confirmations: `research_logs/experiment_outputs/hero_first_place_*.json`
- Extreme-correlation probe: `research_logs/experiment_outputs/extreme_correlation_probe_3c_3s_80m10g_seed64201.json`
- Policy evaluator: `research_logs/experiment_outputs/first_place_policy_eval_post_wta_banding.json` (best fit `68/80`, `0.850`).

4. Validation is green:
- Backend tests: `34/34` pass.
- Web check/build: pass.
- Policy smoke: pass for baseline, WTA pot-pressure, WTA high-stack relief, and 6-player branch.
- Latest integrated preflight (`tests + web + policy smoke`) passed at `2026-03-01 06:56 PST`.

## How to use at game time

1. Start services:
- `uv run uvicorn game.api:app --host 0.0.0.0 --port 8000`
- `pnpm -C web dev --host`

2. Quick validation (recommended):
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke`

3. Apply announced rules:
- `uv run python scripts/day_of_patch.py --preset baseline --overrides-json '<host json>'`

4. Optional empirical lock if time allows:
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '<host json>' --n-tables 12 --n-games 8 --seed 42`

5. In HUD:
- start objective on `ev`, use `Use objective champion`
- log events continuously
- monitor `First-place routing cues` and `resolved_champion_reasons`
- switch to `first_place` only when tournament state needs upside

## Key references

- `research_logs/003_day_of_fast_patch_guide.md`
- `research_logs/004_status_snapshot.md`
- `research_logs/019_pre7_final_checklist.md`
- `research_logs/020_wta_banding_rollout.md`
- `research_logs/001_night_rollout_log.md`

## Latest commits

- `b3d22cc` Record final 06:58 policy smoke readiness check
- `5ef9e69` Sync session n_players state and expand policy smoke checks
- `930cced` Make HUD n_players-aware for day-of variant input
- `bee4a15` Add correlated-pair defensive first-place override
