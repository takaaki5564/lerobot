#!/bin/bash
# Calibrate leader arm (human teleoperation side)
# Updated for latest LeRobot version

# Set port permissions
sudo chmod 666 /dev/ttyACM1

echo "Starting leader arm calibration..."
lerobot-calibrate \
    --robot-type=so100 \
    --robot-port=/dev/ttyACM1 \
    --robot-config-name=my_awesome_leader_arm
