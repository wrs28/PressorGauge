# Deploying to AWS

These notes are primarily for myself, so that I don't forget how I deployed to AWS.
I hope that they may help at least one other person.

This was largely inspired by [this blog post](https://docker-curriculum.com/#introduction) on deploying Docker to AWS.

## Prerequisites

Install `ecs-cli`, instructions [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html).

Install [docker](https://www.docker.com).


## Workflow

Run `aws_build.sh`.

If a new instance is created, make sure to get it's Public DNS (IPv4) and to add an inbound rule to allow my IP address to SSH.
Also, get its IPv4 Public IP address and enter it in AWS Route53 to link the instance to [pressorgauge.com](http://pressorgauge.com).

------------

#### Content of `aws_build.sh`

The first line `source insight` loads in AWS credentials into environmental variables.

Then it builds the docker image and pushes it to [docker hub](https://hub.docker.com) as `wrs28/pressorgauge`.

The next two calls to `ecs-cli configure` set the cluster defaults.

`ecs-cli up` creates the CloudFormation stack, and spins up an instance if it hasn't already been.
If it has, it will throw a warning and skip this step.
This does not affect the deployment.

`ecs-cli compose down` removes any pre-existing **PressorGauge** container, and the final `ecs-cli compose up` starts a container according to `/aws-docker-build/docker-compose.yml`.

#### Content of `/aws-docker-build/docker-compose.yml`

Sensitive credentials stored locally in `.env` file.

Streamlit uses port `8501`, which is rerouted to `80`.
