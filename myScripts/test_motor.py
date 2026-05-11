#!/usr/bin/env python3
"""
Test individual LeKiwi motors one at a time.

Usage:
    python3 test_motor.py
    python3 test_motor.py --port /dev/ttyACM0 --id my_awesome_kiwi --motor arm_gripper
    python3 test_motor.py --motor arm_gripper --value 80

Each motor is moved to a target value and back to zero.
You can also test all motors sequentially by omitting --motor.
"""

import argparse
import time

from lerobot.robots.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig


def test_single_motor(robot, motor_name: str, value: float = 50.0, hold_s: float = 1.5):
    motor_names = list(robot.bus.motors.keys())
    zero = {name: 0.0 for name in motor_names}

    print(f"\n  Testing '{motor_name}' -> {value} ...")
    robot.send_action({**zero, motor_name: value})
    time.sleep(hold_s)

    print(f"  Returning '{motor_name}' -> 0 ...")
    robot.send_action(zero)
    time.sleep(hold_s)
    print(f"  '{motor_name}' OK")


def test_all_motors(robot, value: float = 50.0, hold_s: float = 1.5):
    motor_names = list(robot.bus.motors.keys())
    print(f"\nTesting all {len(motor_names)} motors sequentially (value={value})...")

    for name in motor_names:
        input(f"\n  Press ENTER to test '{name}' ...")
        test_single_motor(robot, name, value, hold_s)

    print("\nAll motors tested successfully!")


def main():
    parser = argparse.ArgumentParser(description="Test individual LeKiwi motors")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--id", default="my_awesome_kiwi", help="Robot ID (default: my_awesome_kiwi)")
    parser.add_argument("--motor", default=None, help="Motor name to test (default: test all)")
    parser.add_argument("--value", type=float, default=50.0, help="Target position value (default: 50)")
    parser.add_argument("--hold", type=float, default=1.5, help="Hold time in seconds (default: 1.5)")
    args = parser.parse_args()

    print(f"Initializing LeKiwi on {args.port}...")
    config = LeKiwiConfig(port=args.port, id=args.id)
    robot = LeKiwi(config)
    robot.connect()

    motor_names = list(robot.bus.motors.keys())
    print(f"Connected! Motors: {motor_names}")

    try:
        if args.motor:
            if args.motor not in motor_names:
                print(f"ERROR: Motor '{args.motor}' not found.")
                print(f"Available motors: {motor_names}")
            else:
                test_single_motor(robot, args.motor, args.value, args.hold)
        else:
            test_all_motors(robot, args.value, args.hold)

    finally:
        print("\nDisconnecting...")
        robot.send_action({name: 0.0 for name in motor_names})
        robot.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
