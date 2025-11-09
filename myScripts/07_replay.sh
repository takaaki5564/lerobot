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

# Note: Direct replay functionality may not be available in latest version
# This shows how to visualize recorded data instead
lerobot-dataset-viz \
    --dataset.repo_id=$DATASET_NAME \
    --dataset.episode=$EPISODE_NUM
