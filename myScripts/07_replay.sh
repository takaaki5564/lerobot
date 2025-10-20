#!/bin/bash
# Replay recorded episodes on the robot
# Updated for latest LeRobot version

# Check HuggingFace username
if [ -z "$HF_USER" ]; then
    echo "Please set HF_USER environment variable to your HuggingFace username"
    echo "Example: export HF_USER=your_username"
    exit 1
fi

DATASET_NAME="${HF_USER}/lerobot-so100-demo"
EPISODE_NUM=${1:-0}

echo "Replaying episode $EPISODE_NUM from dataset $DATASET_NAME"
echo "Make sure the robot is in a safe starting position"
echo "Press ENTER to start replay..."
read

lerobot-eval \
    --policy.path=$DATASET_NAME \
    --policy.device=cpu \
    --env.type=real \
    --env.robot-type=so100 \
    --env.robot-port=/dev/ttyACM0 \
    --env.robot-config-name=my_awesome_follower_arm \
    --eval.n_episodes=1 \
    --eval.batch_size=1
