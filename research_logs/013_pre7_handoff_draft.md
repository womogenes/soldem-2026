# Pre-7 handoff draft

Local time: 2026-03-01 06:34 PST

## Current recommended champion policy

- EV: `equity_evolved_v1`
- robustness: `equity_evolved_v1`
- first-place:
  - exact baseline: `meta_switch`
  - sprint short-stack (`n_orbits<=2` and `start_chips<=150`) only with `winner_takes_all`: `pot_fraction`
  - winner-takes-all pot-pressure (`n_orbits>=3` and (`ante/start>=0.25` or `ante>=50`)): `pot_fraction`
  - winner-takes-all high-stack low-ante (`n_orbits>=3`, `start>=180`, `ante/start<0.20`): `equity_evolved_v1`
  - remaining non-sprint winner-takes-all band: `meta_switch`
  - non-winner-takes-all variants: `equity_evolved_v1`
  - correlated-pair high-confidence table read: `equity_evolved_v1` (defensive override)
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
- Backend tests currently passing: `37/37`.
- Frontend check/build passing.
- HUD input now supports non-5-player variants (`n_players`-aware seat bounds and dynamic stacks).
- Integrated preflight (`tests + web + policy smoke`) passed at `2026-03-01 07:03 PST`.
- Full-stack preflight (`tests + web + policy smoke + bedrock + PB health`) passed at `2026-03-01 06:56 PST`.
- Quick solver and sim runner now support `n_players != 5` (validated by tests and smoke run).
- Policy smoke re-run at `2026-03-01 07:03 PST` passed with expanded winner-takes-all branch + 6-player checks.

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
- `research_logs/020_wta_banding_rollout.md`
- `research_logs/021_pre7_summary.md`

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
- `dd0a087`: integrated full-stack preflight marked as latest readiness check.
- `38e0060`: quick solver and sim runner now support non-5-player variants.
- `99dc4db`: policy smoke expanded with ratio and non-5-player branch checks.
- `747aa79`: winner-takes-all first-place banding update with rollout matrix + hero confirmations.
- `930cced`: HUD input now supports dynamic `n_players` stack/seat handling.
- `bee4a15`: correlated-pair defensive first-place override with extreme-correlation evidence.
- `1eb9bed`: readiness docs refreshed after final preflight and extreme-correlation probe.
- `0054dc7`: final full-stack preflight timestamp refresh (`06:56 PST`).
- `ca4d87d`: final pre-7 handoff doc timestamp and commit-trail sync.
- `5ef9e69`: session/profile `n_players` sync fix + correlated-pair smoke coverage.
- `b3d22cc`: final 06:58 policy-smoke readiness timestamp refresh.
- `01ee7da`: advisor request normalization to active rule-profile bounds.
- `b5e1b20`: readiness docs refreshed after `07:03` integrated preflight.
- `1271c5b`: pre-7 summary refreshed with final readiness commit trail.
