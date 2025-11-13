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
DATASET_NAME="${HF_USER}/record-test2"
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
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=my_awesome_follower_arm \
    --robot.cameras='{"front_close": {"type": "opencv", "index_or_path": /dev/video6, "width": 640, "height": 480, "fps": 30}, "front_wide": {"type": "opencv", "index_or_path": /dev/video4, "width": 640, "height": 480, "fps": 30}}' \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=my_awesome_leader_arm \
    --display_data=false \
    --dataset.repo_id="$DATASET_NAME" \
    --dataset.num_episodes=25 \
    --dataset.episode_time_s=30 \
    --dataset.reset_time_s=10 \
    --dataset.push_to_hub=true \
    --dataset.single_task="$TASK_DESCRIPTION"
