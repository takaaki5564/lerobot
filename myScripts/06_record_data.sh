#!/bin/bash
# Record demonstration data for training
# Updated for latest LeRobot version

# Set your HuggingFace username
if [ -z "$HF_USER" ]; then
    echo "Please set HF_USER environment variable to your HuggingFace username"
    echo "Example: export HF_USER=your_username"
    exit 1
fi

# Dataset name
DATASET_NAME="${HF_USER}/lerobot-so100-demo"
TASK_DESCRIPTION="Pick and place object"

echo "Recording demonstration data..."
echo "Dataset: $DATASET_NAME"
echo "Task: $TASK_DESCRIPTION"
echo "Episodes: 5 episodes of 30 seconds each"
echo ""
echo "Instructions:"
echo "1. Position objects in starting position"
echo "2. Press ENTER to start recording"
echo "3. Perform the task using leader arm"
echo "4. Wait for reset period between episodes"
echo ""

lerobot-record \
    --robot-type=so100 \
    --robot-port=/dev/ttyACM0 \
    --robot-config-name=my_awesome_follower_arm \
    --robot-cameras='{"front": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30}}' \
    --teleop-type=so100 \
    --teleop-port=/dev/ttyACM1 \
    --teleop-config-name=my_awesome_leader_arm \
    --display_data=true \
    --repo-id=$DATASET_NAME \
    --num-episodes=5 \
    --episode-time-s=30 \
    --reset-time-s=10 \
    --fps=30 \
    --push-to-hub=false \
    --single-task="$TASK_DESCRIPTION"
