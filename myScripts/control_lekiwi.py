#!/usr/bin/env python3
"""
Interactive motor control for LeKiwi robot.

Usage:
    python3 control_lekiwi.py
    python3 control_lekiwi.py --port /dev/ttyACM0 --id my_awesome_kiwi

Commands (in interactive mode):
    list                        - List all motor names
    move <motor_name> <value>   - Move a motor (-100 to 100)
    stop                        - Stop all motors
    quit                        - Exit
"""

import argparse

from lerobot.robots.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig


def interactive_control(port: str, robot_id: str):
    print(f"Initializing LeKiwi on {port}...")

    config = LeKiwiConfig(port=port, id=robot_id)
    robot = LeKiwi(config)
    robot.connect()

    motor_names = list(robot.bus.motors.keys())
    zero_action = {name: 0 for name in motor_names}

    print("\nLeKiwi Connected!")
    print(f"Available motors: {motor_names}")
    print("\nCommands:")
    print("  list                      - List all motor names")
    print("  move <motor_name> <value> - Move a motor (-100 to 100)")
    print("  stop                      - Stop all motors")
    print("  quit                      - Exit\n")

    try:
        while True:
            try:
                cmd = input("> ").strip().split()
            except EOFError:
                break

            if not cmd:
                continue

            if cmd[0] == "quit":
                break

            elif cmd[0] == "list":
                print("\nMotors:")
                for name in motor_names:
                    print(f"  - {name}")
                print()

            elif cmd[0] == "stop":
                robot.send_action(zero_action)
                print("All motors stopped.")

            elif cmd[0] == "move" and len(cmd) == 3:
                motor_name, value_str = cmd[1], cmd[2]
                try:
                    value = float(value_str)
                    if motor_name not in motor_names:
                        print(f"Unknown motor: '{motor_name}'. Use 'list' to see available motors.")
                        continue
                    action = {**zero_action, motor_name: value}
                    robot.send_action(action)
                    print(f"  {motor_name} -> {value}")
                except ValueError:
                    print("Value must be a number between -100 and 100.")

            else:
                print("Invalid command. Type 'quit' to exit.")

    finally:
        print("\nStopping motors and disconnecting...")
        robot.send_action(zero_action)
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
