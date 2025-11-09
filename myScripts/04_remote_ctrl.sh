#!/bin/bash
# Teleoperate the follower arm with the leader arm
# Updated for latest LeRobot version

echo "Starting teleoperation..."
echo "Leader arm controls follower arm movements"
echo "Press Ctrl+C to exit"

lerobot-teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM0 \
    --robot.id=my_awesome_follower_arm \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=my_awesome_leader_arm

