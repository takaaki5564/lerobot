#!/bin/bash
# Calibrate follower arm (robot side)
# Updated for latest LeRobot version

# Set port permissions
sudo chmod 666 /dev/ttyACM0

echo "Starting follower arm calibration..."
lerobot-calibrate \
    --robot-type=so100 \
    --robot-port=/dev/ttyACM0 \
    --robot-config-name=my_awesome_follower_arm
