#!/bin/bash
# Teleoperate with camera visualization
# Updated for latest LeRobot version

echo "Starting teleoperation with camera display..."
echo "Camera feed will be shown in real-time"
echo "Press Ctrl+C to exit"

lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=my_awesome_follower_arm \
    --robot.cameras='{"wrist_close": {"type": "opencv", "index_or_path": /dev/video4, "width": 640, "height": 480, "fps": 30}}' \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=my_awesome_leader_arm \
    --display_data=true