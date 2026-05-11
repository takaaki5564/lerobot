#!/usr/bin/env python3
"""
Real-time keyboard control for LeKiwi robot.

Usage:
    python3 keyboard_control_lekiwi.py
    python3 keyboard_control_lekiwi.py --port /dev/ttyACM0 --id my_awesome_kiwi --step 5

Keyboard mapping:
    Arm joints:
        W / S  - Shoulder lift up / down
        A / D  - Shoulder pan left / right
        R / F  - Elbow flex up / down
        T / G  - Wrist flex up / down
        Y / H  - Wrist roll
        Z / X  - Gripper open / close

    Base velocity (body frame):
        I      - Forward  (+x)
        K      - Backward (-x)
        J      - Rotate left  (-theta)
        L      - Rotate right (+theta)
        U      - Strafe left  (-y)
        O      - Strafe right (+y)
        SPACE  - Stop all motors

    Q      - Quit
"""

import argparse
import sys
import termios
import tty

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
BASE_SPEED = 50.0  # Base velocity value when moving


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def clamp(value, lo=-100.0, hi=100.0):
    return max(lo, min(hi, value))


def keyboard_control(port: str, robot_id: str, step: float):
    print(f"Initializing LeKiwi on {port}...")

    config = LeKiwiConfig(port=port, id=robot_id)
    robot = LeKiwi(config)
    robot.connect()

    arm_pos = {m: 0.0 for m in ARM_MOTORS}
    base_vel = {"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 0.0}

    print("\nLeKiwi Keyboard Control — Press Q to quit\n")
    print("  Arm:  W/S=Shoulder lift | A/D=Pan | R/F=Elbow | T/G=Wrist flex | Y/H=Wrist roll | Z/X=Gripper")
    print("  Base: I/K=Fwd/Bwd | J/L=Rotate | U/O=Strafe | SPACE=Stop\n")

    def make_action():
        return {f"{m}.pos": arm_pos[m] for m in ARM_MOTORS} | base_vel

    try:
        while True:
            key = get_key().lower()
            base_vel = {"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 0.0}  # reset base each tick

            if key == "q":
                break
            elif key == " ":
                arm_pos = {m: 0.0 for m in ARM_MOTORS}

            # Arm controls
            elif key == "w":
                arm_pos["arm_shoulder_lift"] = clamp(arm_pos["arm_shoulder_lift"] + step)
            elif key == "s":
                arm_pos["arm_shoulder_lift"] = clamp(arm_pos["arm_shoulder_lift"] - step)
            elif key == "a":
                arm_pos["arm_shoulder_pan"] = clamp(arm_pos["arm_shoulder_pan"] - step)
            elif key == "d":
                arm_pos["arm_shoulder_pan"] = clamp(arm_pos["arm_shoulder_pan"] + step)
            elif key == "r":
                arm_pos["arm_elbow_flex"] = clamp(arm_pos["arm_elbow_flex"] + step)
            elif key == "f":
                arm_pos["arm_elbow_flex"] = clamp(arm_pos["arm_elbow_flex"] - step)
            elif key == "t":
                arm_pos["arm_wrist_flex"] = clamp(arm_pos["arm_wrist_flex"] + step)
            elif key == "g":
                arm_pos["arm_wrist_flex"] = clamp(arm_pos["arm_wrist_flex"] - step)
            elif key == "y":
                arm_pos["arm_wrist_roll"] = clamp(arm_pos["arm_wrist_roll"] + step)
            elif key == "h":
                arm_pos["arm_wrist_roll"] = clamp(arm_pos["arm_wrist_roll"] - step)
            elif key == "z":
                arm_pos["arm_gripper"] = clamp(arm_pos["arm_gripper"] + step)
            elif key == "x":
                arm_pos["arm_gripper"] = clamp(arm_pos["arm_gripper"] - step)

            # Base velocity controls (sent once per keypress, reset next tick)
            elif key == "i":
                base_vel["x.vel"] = BASE_SPEED
            elif key == "k":
                base_vel["x.vel"] = -BASE_SPEED
            elif key == "j":
                base_vel["theta.vel"] = -BASE_SPEED
            elif key == "l":
                base_vel["theta.vel"] = BASE_SPEED
            elif key == "u":
                base_vel["y.vel"] = -BASE_SPEED
            elif key == "o":
                base_vel["y.vel"] = BASE_SPEED
            else:
                continue

            robot.send_action(make_action())
            print(
                f"  arm: pan={arm_pos['arm_shoulder_pan']:+5.0f} "
                f"lift={arm_pos['arm_shoulder_lift']:+5.0f} "
                f"elbow={arm_pos['arm_elbow_flex']:+5.0f} "
                f"wrist_f={arm_pos['arm_wrist_flex']:+5.0f} "
                f"wrist_r={arm_pos['arm_wrist_roll']:+5.0f} "
                f"grip={arm_pos['arm_gripper']:+5.0f}  "
                f"base: x={base_vel['x.vel']:+5.0f} "
                f"y={base_vel['y.vel']:+5.0f} "
                f"θ={base_vel['theta.vel']:+5.0f}   ",
                end="\r",
            )

    finally:
        print("\n\nStopping motors and disconnecting...")
        robot.send_action({f"{m}.pos": 0.0 for m in ARM_MOTORS} | {"x.vel": 0.0, "y.vel": 0.0, "theta.vel": 0.0})
        robot.disconnect()
        print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Keyboard control for LeKiwi robot")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port (default: /dev/ttyACM0)")
    parser.add_argument("--id", default="my_awesome_kiwi", help="Robot ID (default: my_awesome_kiwi)")
    parser.add_argument("--step", type=float, default=5.0, help="Arm position step per keypress (default: 5)")
    args = parser.parse_args()
    keyboard_control(args.port, args.id, args.step)


if __name__ == "__main__":
    main()
