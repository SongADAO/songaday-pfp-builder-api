#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

docker pull python:3.9-alpine

docker compose -f docker-compose.dev.yml down --remove-orphans

docker compose -f docker-compose.dev.yml up -d --build

docker compose -f docker-compose.dev.yml logs -f
