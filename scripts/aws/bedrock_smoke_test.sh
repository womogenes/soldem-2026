#!/usr/bin/env bash
set -euo pipefail

REGION="${1:-us-east-1}"

echo "Listing first 15 Bedrock model IDs in $REGION"
aws bedrock list-foundation-models --region "$REGION" --query 'modelSummaries[0:15].modelId' --output text
