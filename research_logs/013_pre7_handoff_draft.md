# Pre-7 handoff draft

Local time: 2026-03-01 04:34 PST

## Current recommended champion policy

- EV: `equity_evolved_v1`
- robustness: `equity_evolved_v1`
- first-place:
  - exact baseline: `meta_switch`
  - non-baseline variants: `equity_evolved_v1`
  - sprint short-stack (`n_orbits<=2` and `start_chips<=150`) only with `winner_takes_all`: `pot_fraction`
  - high ante pressure winner-takes-all (`n_orbits>=3` and (`ante/start>=0.26` or `ante>=50`)): `pot_fraction`
  - passive high-confidence table read: `pot_fraction`

## Fast day-of commands

0. Optional preflight:
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --pb-url http://18.204.1.6:8090`
- `bash scripts/day_of_preflight.sh --api-url http://127.0.0.1:8000 --with-policy-smoke`

1. Apply profile quickly:
- `uv run python scripts/day_of_patch.py --preset baseline`

2. One-command autosolve and patch:
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --overrides-json '{"n_orbits":2,"start_chips":140,"ante_amt":30}' --n-tables 12 --n-games 8 --seed 42`

3. Keep dynamic resolution after autosolve:
- `uv run python scripts/day_of_autosolve_patch.py --rule-profile baseline_v1 --keep-dynamic`

4. In HUD session panel, verify `First-place routing cues` before game start so trigger assumptions are explicit (`/session/state.first_place_policy_cues`).

## Runtime checks

- Autosolve default runtime benchmark: about `22.9s`.
- Autosolve first-place guardrail default: `first_gap=0.07`.
- Backend tests currently passing: `26/26`.
- Frontend check/build passing.
- Preflight smoke (`API + PocketBase`) passed at `2026-03-01 05:37 PST` with backend tests + web check.
- Policy smoke (`baseline` / `high-ante` / `below-trigger`) passed at `2026-03-01 05:47 PST` after `0.26` threshold update.
- Bedrock smoke passed at `2026-03-01 05:40 PST` (`us-east-1`).

## Latest key docs

- `research_logs/004_status_snapshot.md`
- `research_logs/006_variant_lookup_table.md`
- `research_logs/008_weird_variant_stress.md`
- `research_logs/009_autosolve_guardrail_calibration.md`
- `research_logs/011_horizon_sensitivity.md`
- `research_logs/012_first_place_horizon_check.md`
- `research_logs/016_first_place_fuzz_confirmation.md`
- `research_logs/017_resolver_policy_backtest.md`
- `research_logs/018_ante_threshold_calibration.md`
- `research_logs/019_pre7_final_checklist.md`

## Latest commit checkpoints

- `e861471`: first-place resolver refinement from random-variant confirmations.
- `cc1ba28`: autosolve prior alignment with updated resolver logic.
- `0bbadd0`: resolver backtest evidence docs.
- `62f2fff`: HUD first-place routing cues UI.
- `d382fcd`: preflight + full-suite validation log refresh.
- `9ebf784`: backend-exported first-place policy cues wired into HUD.
- `da6c86a`: ante-threshold calibration and updated high-ante trigger.
- `9492469`: post-calibration full preflight validation log refresh.
- `b71d8bc`: preflight policy smoke checks for first-place routing.
- `d0a6bb9`: high-ante ratio trigger tuned to `0.26` with evaluator-backed evidence.
- `1a62ea5`: Bedrock preflight smoke logged in runbooks.
- `7052415`: handoff checkpoint refresh after `0.26` calibration commit.
- `4aa0808`: human training drills aligned with current policy cues.
- `e73ee05`: final pre-7 countdown checklist added.
- `5be08c0`: HUD reason codes now shown with plain-English descriptions.
