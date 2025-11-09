#!/bin/bash
# Calibrate leader arm (human teleoperation side)
# Updated for latest LeRobot version

# Set port permissions
sudo chmod 666 /dev/ttyACM1

echo "Starting leader arm calibration..."
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=my_awesome_leader_arm
