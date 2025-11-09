#!/bin/bash
# Calibrate follower arm (robot side)
# Updated for latest LeRobot version

# Set port permissions
sudo chmod 666 /dev/ttyACM0

echo "Starting follower arm calibration..."
lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=my_awesome_follower_arm
