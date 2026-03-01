# Mode switch policy for day-of play

Local timestamp: 2026-03-01 07:10:47 PST

## Purpose

Choose between aggressive EV mode and conservative fallback mode in real time.

## Artifacts

- Aggressive EV-leaning artifact:
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-071000-merged4.json`
- Conservative fallback artifact:
- `research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json`

## Recommended default

- Use aggressive merged3 split:
- `ev=5400/0.032/2`, `first_place=seller_profit`, `robustness=4500/0.02/2`

## Switch to conservative fallback when

- You observe frequent coordinated bids or soft-collusion behavior.
- EV edge from aggressive mode appears unstable after first 2-3 games.
- You need to protect a lead and reduce downside variance.

## Trigger rules

- If bankroll drops by more than one full ante stack over 2 games, switch to fallback.
- If two opponents repeatedly avoid bidding against each other, switch to fallback.
- If you are in top-2 standings with 3 or fewer games left, use fallback unless a high-upside comeback is needed.

## Fast switch commands

Load aggressive merged4:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path":"research_logs/experiment_outputs/distributed_upgrade_validation_20260301-071000-merged4.json"}'
```

Load conservative safe fallback:

```bash
curl -sS -X POST http://127.0.0.1:8000/strategies/load_champions \
  -H 'content-type: application/json' \
  -d '{"summary_path":"research_logs/experiment_outputs/distributed_upgrade_validation_20260301-064350-safe.json"}'
```
