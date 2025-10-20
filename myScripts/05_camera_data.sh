#!/bin/bash
# Teleoperate with camera visualization
# Updated for latest LeRobot version

echo "Starting teleoperation with camera display..."
echo "Camera feed will be shown in real-time"
echo "Press Ctrl+C to exit"

lerobot-teleoperate \
    --robot-type=so100 \
    --robot-port=/dev/ttyACM0 \
    --robot-config-name=my_awesome_follower_arm \
    --robot-cameras='{"front": {"type": "opencv", "index_or_path": 0, "width": 1920, "height": 1080, "fps": 30}}' \
    --teleop-type=so100 \
    --teleop-port=/dev/ttyACM1 \
    --teleop-config-name=my_awesome_leader_arm \
    --display_data=true