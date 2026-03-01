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
