# Day-of runbook

Local timestamp: 2026-03-01 03:10:00 PST

## Startup

1. Start API.

```bash
uv run uvicorn game.api:app --host 127.0.0.1 --port 8000
```

2. Start HUD.

```bash
pnpm --dir web dev --host 127.0.0.1 --port 5173
```

3. Open `http://127.0.0.1:5173`.

## Live loop

- Enter phase, stacks, your cards, auction cards, and known cards.
- Keep objective on `ev` unless standings pressure suggests `first_place` or `robustness`.
- Log bids/auction/showdown events in the side panel.
- Use recommendation as default action, then override for table dynamics.

## Objective defaults

- `ev`: `market_maker_tight`
- `first_place`: `market_maker_tight`
- `robustness`: `regime_switch_robust`

## Optional high-variance mode

- If you are late in standings and need upside over expectation, set strategy tag manually to `pot_fraction`.
- Use this sparingly: simulations show higher first-place rate but materially worse expected PnL.

## Quick checks

### API health

```bash
curl -s http://127.0.0.1:8000/health
```

### Session/champion state

```bash
curl -s http://127.0.0.1:8000/session/state
```

### Emergency reset

```bash
curl -s -X POST http://127.0.0.1:8000/session/reset
```

## Compaction note

Future compaction/handoff runs should always include `research_logs/000_god_prompt.md` as a required context reference.
