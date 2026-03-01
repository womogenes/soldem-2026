# Bedrock latency probe

Local time: 2026-03-01 03:09 PST

## What was tested

- Bedrock model listing in `us-east-1` using `scripts/aws/bedrock_smoke_test.sh`.
- Runtime latency via `scripts/aws/bedrock_latency_probe.sh`.

## Findings

1. Bedrock API access is available from this environment.
2. New Anthropic model IDs require inference profiles (direct on-demand model ID invocation can fail).
3. Working default profile:
- `us.anthropic.claude-3-5-haiku-20241022-v1:0`

Observed latency sample:
- call_1: 6821 ms (cold-ish)
- call_2: 1767 ms
- call_3: 1912 ms
- average: 3500 ms

## Implication for day-of

- LLM fallback is feasible within a 10-second turn budget if limited to short prompts and profile-based invocation.
- Keep deterministic local strategy as primary; use LLM as optional second-opinion/fallback where needed.

## Commands

Model availability:
`bash scripts/aws/bedrock_smoke_test.sh us-east-1`

Latency probe:
`bash scripts/aws/bedrock_latency_probe.sh us-east-1`
