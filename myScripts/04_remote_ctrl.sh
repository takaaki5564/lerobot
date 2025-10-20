#!/bin/bash
# Teleoperate the follower arm with the leader arm
# Updated for latest LeRobot version

echo "Starting teleoperation..."
echo "Leader arm controls follower arm movements"
echo "Press Ctrl+C to exit"

lerobot-teleoperate \
    --robot-type=so100 \
    --robot-port=/dev/ttyACM0 \
    --robot-config-name=my_awesome_follower_arm \
    --teleop-type=so100 \
    --teleop-port=/dev/ttyACM1 \
    --teleop-config-name=my_awesome_leader_arm

