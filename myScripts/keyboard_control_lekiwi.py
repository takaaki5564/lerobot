#!/usr/bin/env python3
"""
Real-time keyboard control for LeKiwi robot.

Usage:
    python3 keyboard_control_lekiwi.py
    python3 keyboard_control_lekiwi.py --port /dev/ttyACM0 --id my_awesome_kiwi

Keyboard mapping:
    Arm:
        W / S  - Shoulder lift up / down
        A / D  - Shoulder pan left / right
        R / F  - Elbow flex up / down
        T / G  - Wrist flex up / down
        Y / H  - Wrist roll
        Z / X  - Gripper open / close

    Base (mobile wheels):
        I      - Forward
        K      - Backward
        J      - Rotate left
        L      - Rotate right
        SPACE  - Stop all motors

    Q      - Quit
"""

import argparse
import sys
import termios
import tty

from lerobot.robots.lekiwi import LeKiwi
from lerobot.robots.lekiwi.config_lekiwi import LeKiwiConfig

STEP = 5  # Position step size per keypress


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def clamp(value, lo=-100, hi=100):
    return max(lo, min(hi, value))


def keyboard_control(port: str, robot_id: str):
    print(f"Initializing LeKiwi on {port}...")

    config = LeKiwiConfig(port=port, id=robot_id)
    robot = LeKiwi(config)
    robot.connect()

    pos = {name: 0.0 for name in robot.bus.motors.keys()}

    print("\nLeKiwi Keyboard Control — Press Q to quit\n")
    print("  Arm:  W/S=Shoulder lift | A/D=Pan | R/F=Elbow | T/G=Wrist flex | Y/H=Wrist roll | Z/X=Gripper")
    print("  Base: I=Forward | K=Backward | J=Left | L=Right | SPACE=Stop\n")

    try:
        while True:
            key = get_key().lower()

            if key == "q":
                break

            # Arm
            elif key == "w":
                pos["arm_shoulder_lift"] = clamp(pos["arm_shoulder_lift"] + STEP)
            elif key == "s":
                pos["arm_shoulder_lift"] = clamp(pos["arm_shoulder_lift"] - STEP)
            elif key == "a":
                pos["arm_shoulder_pan"] = clamp(pos["arm_shoulder_pan"] - STEP)
            elif key == "d":
                pos["arm_shoulder_pan"] = clamp(pos["arm_shoulder_pan"] + STEP)
            elif key == "r":
                pos["arm_elbow_flex"] = clamp(pos["arm_elbow_flex"] + STEP)
            elif key == "f":
                pos["arm_elbow_flex"] = clamp(pos["arm_elbow_flex"] - STEP)
            elif key == "t":
                pos["arm_wrist_flex"] = clamp(pos["arm_wrist_flex"] + STEP)
            elif key == "g":
                pos["arm_wrist_flex"] = clamp(pos["arm_wrist_flex"] - STEP)
            elif key == "y":
                pos["arm_wrist_roll"] = clamp(pos["arm_wrist_roll"] + STEP)
            elif key == "h":
                pos["arm_wrist_roll"] = clamp(pos["arm_wrist_roll"] - STEP)
            elif key == "z":
                pos["arm_gripper"] = clamp(pos["arm_gripper"] + STEP)
            elif key == "x":
                pos["arm_gripper"] = clamp(pos["arm_gripper"] - STEP)

            # Base
            elif key == "i":
                pos["base_left_wheel"] = 50
                pos["base_back_wheel"] = 50
                pos["base_right_wheel"] = 50
            elif key == "k":
                pos["base_left_wheel"] = -50
                pos["base_back_wheel"] = -50
                pos["base_right_wheel"] = -50
            elif key == "j":
                pos["base_left_wheel"] = -40
                pos["base_back_wheel"] = 0
                pos["base_right_wheel"] = 40
            elif key == "l":
                pos["base_left_wheel"] = 40
                pos["base_back_wheel"] = 0
                pos["base_right_wheel"] = -40
            elif key == " ":
                pos = {name: 0.0 for name in robot.bus.motors.keys()}

            else:
                continue

            robot.send_action(pos)
            print(f"  arm: pan={pos['arm_shoulder_pan']:+.0f} lift={pos['arm_shoulder_lift']:+.0f} "
                  f"elbow={pos['arm_elbow_flex']:+.0f} wrist_f={pos['arm_wrist_flex']:+.0f} "
                  f"wrist_r={pos['arm_wrist_roll']:+.0f} grip={pos['arm_gripper']:+.0f}  "
                  f"base: L={pos['base_left_wheel']:+.0f} B={pos['base_back_wheel']:+.0f} "
                  f"R={pos['base_right_wheel']:+.0f}   ", end="\r")

    finally:
        print("\n\nStopping motors and disconnecting...")
        robot.send_action({name: 0.0 for name in robot.bus.motors.keys()})
        robot.disconnect()
        print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Keyboard control for LeKiwi robot")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--id", default="my_awesome_kiwi", help="Robot ID (default: my_awesome_kiwi)")
    args = parser.parse_args()
    keyboard_control(args.port, args.id)


if __name__ == "__main__":
    main()
