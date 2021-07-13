#!/bin/bash

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

aws eks update-kubeconfig --name surreal-dev

if [[ "$1" == "server" ]];
then
    gunicorn -c /workspace/gunicorn.py starks.wsgi:application
elif [[ "$1" == "vqgan-dispatcher" ]];
then
    python /workspace/starks/modules/vqgan/dispatcher.py
fi
