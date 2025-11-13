#!/bin/bash

DATASET_NAME="${HF_USER}/eval_so101-test2"
TASK_DESCRIPTION="Pick and place object"

echo "Run inference and evaluate your policy"
echo "Dataset: $DATASET_NAME"
echo "Task: $TASK_DESCRIPTION"
echo ""

lerobot-record  \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
    --robot.cameras='{"front_close": {"type": "opencv", "index_or_path": /dev/video6, "width": 640, "height": 480, "fps": 30}, "front_wide": {"type": "opencv", "index_or_path": /dev/video4, "width": 640, "height": 480, "fps": 30}}' \
  --robot.id=my_awesome_follower_arm \
  --display_data=false \
  --dataset.repo_id="${DATASET_NAME}" \
  --dataset.single_task="${TASK_DESCRIPTION}" \
  --policy.path=${HF_USER}/record-test2 \
  2>&1 | tee inference_log.txt

  # <- Teleop optional if you want to teleoperate in between episodes \
  # --teleop.type=so100_leader \
  # --teleop.port=/dev/ttyACM0 \
  # --teleop.id=my_awesome_leader_arm \
