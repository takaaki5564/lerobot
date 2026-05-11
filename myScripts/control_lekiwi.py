#!/usr/bin/env python3
"""
Interactive motor control for LeKiwi robot.

Usage:
    python3 control_lekiwi.py
    python3 control_lekiwi.py --port /dev/ttyACM0 --id my_awesome_kiwi

Action format:
    Arm positions (range -100 to 100):
        arm_shoulder_pan, arm_shoulder_lift, arm_elbow_flex,
        arm_wrist_flex, arm_wrist_roll, arm_gripper

    Base velocity (range -100 to 100):
        x     - forward(+) / backward(-)
        y     - strafe left(-) / right(+)
        theta - rotate left(-) / right(+)

Commands:
    list                   - List all available controls
    arm <name> <value>     - Move an arm joint (e.g. arm gripper 80)
    base <x> <y> <theta>   - Set base velocity
    stop                   - Stop all motors
    quit                   - Exit
"""

import argparse

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

ZERO_ACTION = {f"{m}.pos": 0.0 for m in ARM_MOTORS} | {"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 0.0}


def interactive_control(port: str, robot_id: str):
    print(f"Initializing LeKiwi on {port}...")

    config = LeKiwiConfig(port=port, id=robot_id)
    robot = LeKiwi(config)
    robot.connect()

    print("\nLeKiwi Connected!")
    print("\nCommands:")
    print("  list                  - List all available controls")
    print("  arm <name> <value>    - Move an arm joint (-100 to 100)")
    print("  base <x> <y> <theta>  - Set base velocity (-100 to 100)")
    print("  stop                  - Stop all motors")
    print("  quit                  - Exit")
    print("\nArm joints:", ARM_MOTORS)
    print("Base axes:  x (fwd/bwd), y (strafe), theta (rotate)\n")

    try:
        while True:
            try:
                cmd = input("> ").strip().split()
            except EOFError:
                break

            if not cmd:
                continue

            elif cmd[0] == "quit":
                break

            elif cmd[0] == "list":
                print("\nArm joints (use 'arm <name> <value>'):")
                for m in ARM_MOTORS:
                    print(f"  {m}")
                print("\nBase velocity (use 'base <x> <y> <theta>'):")
                print("  x     = forward(+) / backward(-)")
                print("  y     = strafe right(+) / left(-)")
                print("  theta = rotate right(+) / left(-)\n")

            elif cmd[0] == "stop":
                robot.send_action(ZERO_ACTION)
                print("All motors stopped.")

            elif cmd[0] == "arm" and len(cmd) == 3:
                name, value_str = cmd[1], cmd[2]
                if name not in ARM_MOTORS:
                    print(f"Unknown arm joint: '{name}'. Available: {ARM_MOTORS}")
                    continue
                try:
                    value = float(value_str)
                    action = {**ZERO_ACTION, f"{name}.pos": value}
                    robot.send_action(action)
                    print(f"  {name}.pos -> {value}")
                except ValueError:
                    print("Value must be a number between -100 and 100.")

            elif cmd[0] == "base" and len(cmd) == 4:
                try:
                    x, y, theta = float(cmd[1]), float(cmd[2]), float(cmd[3])
                    action = {**ZERO_ACTION, "x.vel": x, "y.vel": y, "theta.vel": theta}
                    robot.send_action(action)
                    print(f"  base vel -> x={x} y={y} theta={theta}")
                except ValueError:
                    print("Values must be numbers. Usage: base <x> <y> <theta>")

            else:
                print("Invalid command. Type 'list' to see available controls.")

    finally:
        print("\nStopping motors and disconnecting...")
        robot.send_action(ZERO_ACTION)
        robot.disconnect()
        print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Interactive LeKiwi motor control")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--id", default="my_awesome_kiwi", help="Robot ID (default: my_awesome_kiwi)")
    args = parser.parse_args()
    interactive_control(args.port, args.id)


if __name__ == "__main__":
    main()
