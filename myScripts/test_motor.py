#!/usr/bin/env python3
"""
Test individual LeKiwi motors one at a time.

Usage:
    python3 test_motor.py
    python3 test_motor.py --motor arm_gripper
    python3 test_motor.py --motor arm_gripper --value 80
    python3 test_motor.py --base x  # Test base forward/backward

Available arm motors:
    arm_shoulder_pan, arm_shoulder_lift, arm_elbow_flex,
    arm_wrist_flex, arm_wrist_roll, arm_gripper

Available base axes:
    x (forward/backward), y (strafe), theta (rotate)
"""

import argparse
import time

from lerobot.robots.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig

ARM_MOTORS = [
    "arm_shoulder_pan",
    "arm_shoulder_lift",
    "arm_elbow_flex",
    "arm_wrist_flex",
    "arm_wrist_roll",
    "arm_gripper",
]
BASE_AXES = ["x", "y", "theta"]
ZERO_ACTION = {f"{m}.pos": 0.0 for m in ARM_MOTORS} | {"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 0.0}


def test_arm_motor(robot, motor_name: str, value: float, hold_s: float):
    print(f"\n  Testing arm joint '{motor_name}' -> {value} ...")
    robot.send_action({**ZERO_ACTION, f"{motor_name}.pos": value})
    time.sleep(hold_s)
    print(f"  Returning '{motor_name}' -> 0 ...")
    robot.send_action(ZERO_ACTION)
    time.sleep(hold_s)
    print(f"  '{motor_name}' OK")


def test_base_axis(robot, axis: str, value: float, hold_s: float):
    print(f"\n  Testing base '{axis}.vel' -> {value} ...")
    robot.send_action({**ZERO_ACTION, f"{axis}.vel": value})
    time.sleep(hold_s)
    print(f"  Stopping base ...")
    robot.send_action(ZERO_ACTION)
    time.sleep(hold_s)
    print(f"  base '{axis}' OK")


def test_all(robot, value: float, hold_s: float):
    print(f"\nTesting all arm joints (value={value}, hold={hold_s}s)...")
    for name in ARM_MOTORS:
        input(f"\n  Press ENTER to test arm joint '{name}' ...")
        test_arm_motor(robot, name, value, hold_s)

    print(f"\nTesting all base axes (value={value}, hold={hold_s}s)...")
    for axis in BASE_AXES:
        input(f"\n  Press ENTER to test base '{axis}.vel' ...")
        test_base_axis(robot, axis, value, hold_s)

    print("\nAll motors tested successfully!")


def main():
    parser = argparse.ArgumentParser(description="Test individual LeKiwi motors")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--id", default="my_awesome_kiwi", help="Robot ID (default: my_awesome_kiwi)")
    parser.add_argument("--motor", default=None, choices=ARM_MOTORS, help="Arm motor to test")
    parser.add_argument("--base", default=None, choices=BASE_AXES, help="Base axis to test (x, y, theta)")
    parser.add_argument("--value", type=float, default=50.0, help="Target value (default: 50)")
    parser.add_argument("--hold", type=float, default=1.5, help="Hold time in seconds (default: 1.5)")
    args = parser.parse_args()

    print(f"Initializing LeKiwi on {args.port}...")
    robot = LeKiwi(LeKiwiConfig(port=args.port, id=args.id))
    robot.connect()
    print("Connected!")

    try:
        if args.motor:
            test_arm_motor(robot, args.motor, args.value, args.hold)
        elif args.base:
            test_base_axis(robot, args.base, args.value, args.hold)
        else:
            test_all(robot, args.value, args.hold)
    finally:
        print("\nDisconnecting...")
        robot.send_action(ZERO_ACTION)
        robot.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
