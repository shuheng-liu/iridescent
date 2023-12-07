#!/bin/bash
set -e
if [ $# -ne 2 ]; then
  echo "Usage: ./run_docker.sh <IRIS_IMAGE>:<TAG> <IRIS_INSTANCE>"
  exit 1
fi
echo "FROM $1" > Dockerfile.temporary
cat ./docker/Dockerfile.template >> Dockerfile.temporary
docker build -t iridescent --build-arg IRIS_INSTANCE="$2" -f Dockerfile.temporary  .
docker container run --rm -it --name iridescent iridescent