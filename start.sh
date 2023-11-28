#!/usr/bin/bash

# Change name also in stop.sh
TMUX_NAME=owlvit-tmux
DOCKER_CONTAINER_NAME=owl-vit-container

echo "Start this script inside the jax root folder"
usage() { echo "Usage: $0 [-b (just bash)]" 1>&2; exit 1; }

while getopts b flag
do
    case "${flag}" in
        b) JUST_BASH='1';;
    esac
done

# Start the container with the right options
docker run --gpus=all -v "$(pwd)":/home/owlvit/project -itd --rm \
--gpus=all \
--env DISPLAY=:0 \
--env QT_X11_NO_MITSHM=1 --env XDG_RUNTIME_DIR=/root/1000 --env XAUTHORITY=/root/.Xauthority -v "${XAUTHORITY}":/root/.Xauthority:rw \
--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
--ipc=host \
--network=host --name $DOCKER_CONTAINER_NAME  owl-vit bash

# Create tmux session
tmux new-session -d -s $TMUX_NAME
tmux set-option -t $TMUX_NAME status-left-length 140
tmux set -t $TMUX_NAME -g pane-border-status top
tmux set -t $TMUX_NAME -g mouse on

# Just bash
if [ -n "$JUST_BASH" ] # Variable is non-null
then
  tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
  tmux a -t $TMUX_NAME
  exit 0
fi


tmux rename-window -t $TMUX_NAME components

# Owl-Vit
tmux select-pane -T "Owl-ViT"
tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
tmux send-keys -t $TMUX_NAME "python detector/detector.py" Enter

tmux split-window -h -t $TMUX_NAME

# Clip Textual Branch
tmux select-pane -T "CLIP Text"
tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
tmux send-keys -t $TMUX_NAME "python detector/ensamble_embeddings.py" Enter

tmux select-layout -t $TMUX_NAME tiled
tmux new-window -t $TMUX_NAME
tmux rename-window -t $TMUX_NAME input/output

# Source
tmux select-pane -T "Source"
tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
tmux send-keys -t $TMUX_NAME "python src/source.py" Enter
tmux split-window -h -t $TMUX_NAME

# Sink
tmux select-pane -T "Sink"
tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
tmux send-keys -t $TMUX_NAME "python gui/main.py" Enter

tmux select-layout -t $TMUX_NAME tiled
tmux new-window -t $TMUX_NAME
tmux rename-window -t $TMUX_NAME communication

# Manager
tmux select-pane -T "Manager"
tmux send-keys -t $TMUX_NAME "docker exec -it $DOCKER_CONTAINER_NAME bash" Enter
tmux send-keys -t $TMUX_NAME "python src/manager.py" Enter
tmux split-window -h -t $TMUX_NAME

tmux select-layout -t $TMUX_NAME tiled

# Attach
tmux select-window -t "components"
tmux a -t $TMUX_NAME
