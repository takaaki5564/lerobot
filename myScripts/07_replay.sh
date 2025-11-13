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

lerobot-replay \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=my_awesome_follower_arm \
    --dataset.repo_id=${HF_USER}/record-test2 \
    --dataset.episode=0 # choose the episode you want to replay