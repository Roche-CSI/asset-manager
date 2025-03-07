#!/bin/bash

IMAGE_NAME="asset-dashboard-react"
HOST_PORT=0.0.0.0:443
CONTAINER_PORT=3000
HOST_CERTS_PATH="/cert"
MOUNT_CERTS_PATH="/cert"

function build_ui_app() {
    # build ui app
    cd ui_app || exit
    rm -rf ./dist # remove old builds
    npm run build
    cd .. || exit
}

function build_node_app() {
    # build node app
    cd node_app || exit
    rm -rf ./dist # remove old builds
    npm run build
    cd .. || exit
    docker build -t $IMAGE_NAME --no-cache .
}

function build_image() {
  build_type=$1
  if [[ $build_type == "node" ]]; then
    # build node app only
    build_node_app
  else
    # build both
    build_ui_app
    build_node_app
  fi
}

function run_image() {
  echo "running on port ${HOST_PORT}"
  docker run \
    --mount type=bind,source="${HOST_CERTS_PATH}",target="${MOUNT_CERTS_PATH}" \
    --detach \
    --publish $HOST_PORT:$CONTAINER_PORT "${IMAGE_NAME}:latest"
#  docker run -d -it -p  $port:$CONTAINER_PORT $IMAGE_NAME
}

ACTION=$1

if [[ $ACTION == "build" ]]; then
  echo "building docker image..."
  build_image "${2}"
elif [[ $ACTION == "run" ]]; then
  echo "running docker image..."
  run_image "${2}" # port
else
  echo "unknown command"
fi