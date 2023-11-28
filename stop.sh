#!/bin/bash

TMUX_NAME=owlvit-tmux
DOCKER_IMAGE_NAME=owl-vit-container

docker rm -f $DOCKER_IMAGE_NAME
tmux kill-session -t $TMUX_NAME