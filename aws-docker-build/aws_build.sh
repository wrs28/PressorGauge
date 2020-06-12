#!/bin/bash

source insight

cd ~/Documents/insight/PressorGauge/aws-docker-build

docker build -t wrs28/pressorgauge ..

docker push wrs28/pressorgauge

PROFILE=pressorgauge

ecs-cli configure profile\
  --profile-name $PROFILE\
  --access-key $AWS_ACCESS_KEY_ID\
  --secret-key $AWS_SECRET_ACCESS_KEY

ecs-cli configure\
  --region us-east-1\
  --cluster $PROFILE\
  --default-launch-type EC2

ecs-cli up \
  --keypair pressorgauge\
  --capability-iam\
  --size 1\
  --instance-type m5ad.xlarge\
  --vpc vpc-0282c7fb91f8ccbc9\
  --subnets subnet-040d66d7c35fcf2d7, subnet-0636ee9001d20849e, subnet-07a8335fe325a6f64, subnet-08142dcdb2e3dca62, subnet-085b5bae67cbfbeca, subnet-0ab3cea7b01ed69c8\
  --security-group sg-0cda1e89d38933d70

sleep 5

ecs-cli compose down

sleep 5

ecs-cli compose up
