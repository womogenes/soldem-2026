#!/usr/bin/env bash
set -euo pipefail

# Provision a PocketBase EC2 host in us-east-1.
# Usage:
#   scripts/aws/provision_pocketbase_ec2.sh --key-name my-key --name soldem-pocketbase

REGION="us-east-1"
INSTANCE_TYPE="t3.small"
NAME="soldem-pocketbase"
KEY_NAME=""
ALLOW_CIDR="0.0.0.0/0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --region) REGION="$2"; shift 2;;
    --instance-type) INSTANCE_TYPE="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    --key-name) KEY_NAME="$2"; shift 2;;
    --allow-cidr) ALLOW_CIDR="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$KEY_NAME" ]]; then
  echo "--key-name is required"
  exit 1
fi

VPC_ID=$(aws ec2 describe-vpcs --region "$REGION" --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --region "$REGION" --filters Name=default-for-az,Values=true --query 'Subnets[0].SubnetId' --output text)

SG_NAME="${NAME}-sg"
SG_ID=$(aws ec2 describe-security-groups --region "$REGION" --filters "Name=group-name,Values=${SG_NAME}" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)
if [[ -z "$SG_ID" || "$SG_ID" == "None" ]]; then
  SG_ID=$(aws ec2 create-security-group \
    --region "$REGION" \
    --group-name "$SG_NAME" \
    --description "Soldem PocketBase SG" \
    --vpc-id "$VPC_ID" \
    --query GroupId --output text)
fi

aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 22 --cidr "$ALLOW_CIDR" 2>/dev/null || true
aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 8090 --cidr "$ALLOW_CIDR" 2>/dev/null || true

AMI_ID=$(aws ssm get-parameter \
  --region "$REGION" \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameter.Value' --output text)

read -r -d '' USER_DATA <<'EOF' || true
#!/bin/bash
set -euxo pipefail
cd /opt
curl -L -o pocketbase.zip https://github.com/pocketbase/pocketbase/releases/download/v0.27.2/pocketbase_0.27.2_linux_amd64.zip
unzip -o pocketbase.zip -d /opt/pocketbase
mkdir -p /opt/pocketbase/pb_data
cat >/etc/systemd/system/pocketbase.service <<SERVICE
[Unit]
Description=PocketBase
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/pocketbase
ExecStart=/opt/pocketbase/pocketbase serve --http=0.0.0.0:8090
Restart=always
User=root

[Install]
WantedBy=multi-user.target
SERVICE
systemctl daemon-reload
systemctl enable pocketbase
systemctl start pocketbase
EOF

INSTANCE_ID=$(aws ec2 run-instances \
  --region "$REGION" \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --subnet-id "$SUBNET_ID" \
  --associate-public-ip-address \
  --user-data "$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$NAME}]" \
  --query 'Instances[0].InstanceId' --output text)

aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "instance_id=$INSTANCE_ID"
echo "public_ip=$PUBLIC_IP"
echo "pocketbase_url=http://$PUBLIC_IP:8090"
