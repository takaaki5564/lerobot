#!/usr/bin/env python3
"""
Debug script to diagnose why LeKiwi base motors (7, 8, 9) are not moving.

Usage:
    python3 myScripts/debug_base_motors.py
    python3 myScripts/debug_base_motors.py --port /dev/ttyACM0

This script checks:
1. Which motors are detected on the bus
2. Whether base motors are in VELOCITY mode
3. What raw values are sent for a given velocity command
4. Whether direct sync_write to base motors works
"""

import argparse
import time

from lerobot.robots.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig

BASE_MOTORS = ["base_left_wheel", "base_back_wheel", "base_right_wheel"]


def debug_base_motors(port: str, robot_id: str):
    print(f"\n{'='*60}")
    print("LeKiwi Base Motor Debug")
    print(f"{'='*60}\n")

    # --- Step 1: Scan the bus ---
    print("Step 1: Scanning bus for motors...")
    from lerobot.motors.feetech import FeetechMotorsBus
    found = FeetechMotorsBus.scan_port(port)
    if found:
        for baudrate, ids in found.items():
            print(f"  Baudrate {baudrate}: Found IDs {ids}")
    else:
        print("  ✗ No motors found!")
    print()

    # --- Step 2: Connect the robot ---
    print("Step 2: Connecting LeKiwi robot...")
    config = LeKiwiConfig(port=port, id=robot_id)
    robot = LeKiwi(config)
    robot.connect()
    print("  ✓ Robot connected\n")

    bus = robot.bus

    # --- Step 3: Check Operating Mode ---
    print("Step 3: Checking operating mode of base motors...")
    try:
        for name in BASE_MOTORS:
            mode = bus.read("Operating_Mode", name)
            mode_label = "VELOCITY(1) ✓" if mode == 1 else f"NOT VELOCITY ({mode}) ✗"
            print(f"  {name}: mode = {mode_label}")
    except Exception as e:
        print(f"  ✗ Failed to read operating mode: {e}")
    print()

    # --- Step 4: Show raw velocity values for a forward command ---
    print("Step 4: Computing raw wheel velocities for x=50 m/s forward...")
    raw_vel = robot._body_to_wheel_raw(x=50.0, y=0.0, theta=0.0)
    for name, val in raw_vel.items():
        print(f"  {name}: raw={val}")
    print()

    # --- Step 5: Direct velocity command ---
    print("Step 5: Sending direct velocity command to each base motor...")
    print("  (Each motor will spin for 2 seconds, then stop)\n")

    for name in BASE_MOTORS:
        motor_id = bus.motors[name].id
        print(f"  Testing {name} (ID={motor_id})...")
        try:
            input(f"    Press ENTER to spin '{name}' forward...")
            bus.sync_write("Goal_Velocity", {name: 1000}, normalize=False)
            time.sleep(2.0)
            bus.sync_write("Goal_Velocity", {name: 0}, normalize=False)
            print(f"    ✓ Command sent. Did '{name}' move? (yes/no)")
            response = input("    > ").strip().lower()
            if response == "yes":
                print(f"    ✓ {name} is working!")
            else:
                print(f"    ✗ {name} did not move — possible hardware issue")
        except Exception as e:
            print(f"    ✗ Error sending command to {name}: {e}")
        print()

    # --- Step 6: Full forward command via send_action ---
    print("Step 6: Testing full forward command via send_action (x=50, y=0, theta=0)...")
    input("  Press ENTER to send forward command for 2 seconds...")
    try:
        action = {
            "arm_shoulder_pan.pos": 0.0,
            "arm_shoulder_lift.pos": 0.0,
            "arm_elbow_flex.pos": 0.0,
            "arm_wrist_flex.pos": 0.0,
            "arm_wrist_roll.pos": 0.0,
            "arm_gripper.pos": 0.0,
            "x.vel": 50.0,
            "y.vel": 0.0,
            "theta.vel": 0.0,
        }
        robot.send_action(action)
        time.sleep(2.0)

        # Stop
        stop_action = {k: 0.0 for k in action}
        robot.send_action(stop_action)
        print("  ✓ Command sent. Did the base move forward?")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\nDisconnecting...")
    robot.disconnect()
    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Debug LeKiwi base motors")
    parser.add_argument("--port", default="/dev/ttyACM0")
    parser.add_argument("--id", default="my_awesome_kiwi")
    args = parser.parse_args()
    debug_base_motors(args.port, args.id)


if __name__ == "__main__":
    main()
