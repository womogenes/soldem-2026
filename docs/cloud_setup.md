# Cloud setup for PocketBase and worker swarm

Local timestamp: 2026-03-01 01:27 PST

Default region is `us-east-1`.

## PocketBase host

```bash
scripts/aws/provision_pocketbase_ec2.sh --key-name <ec2-key-name> --name soldem-pocketbase
```

Outputs include `instance_id`, `public_ip`, and `pocketbase_url`.

## Worker swarm

```bash
scripts/aws/launch_worker_swarm.sh \
  --key-name <ec2-key-name> \
  --repo <git-url> \
  --branch main \
  --pocketbase-url http://<public-ip>:8090 \
  --count 4
```

## Bedrock smoke test

```bash
scripts/aws/bedrock_smoke_test.sh us-east-1
```

## Push experiment outputs into PocketBase

```bash
python scripts/push_results_to_pocketbase.py \
  research_logs/experiment_outputs/long_parallel_matrix_20260301_012847.json \
  --base-url http://<public-ip>:8090 \
  --admin-token <admin-token> \
  --rule-profile baseline_v1 \
  --objective ev
```

## Cost controls

- Use small `COUNT` and short experiment windows first.
- Terminate all worker instances after batch completion.
- Keep a running spend check:
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d 'today' +%Y-%m-%d),End=$(date -d 'tomorrow' +%Y-%m-%d) \
  --granularity DAILY \
  --metrics UnblendedCost
```
