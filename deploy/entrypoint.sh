#!/bin/sh

set -e

mkdir -p ~/.aws

cat << EOF > ~/.aws/credentials
[default]
aws_access_key_id = $AWS_ACCESS_KEY
aws_secret_access_key = $AWS_SECRET_KEY
EOF

cat << EOF > ~/.aws/config
[default]
output = json
region = $AWS_REGION
EOF

python /init-kube-config.py
aws eks update-kubeconfig --name surreal-dev

gunicorn -c /workspace/gunicorn.conf starks.wsgi:application
