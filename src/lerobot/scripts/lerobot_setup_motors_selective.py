#!/usr/bin/env python

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Helper to set motor ids and baudrate with skip functionality.

This script allows you to:
1. Set up all motors interactively (skip ones already configured)
2. Set up only specific motors by name
3. Scan to find motors on the port

Examples:

```shell
# Interactive mode - skip any motor you don't want to configure
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0

# Configure only specific motors
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --motors=shoulder,elbow

# Scan for motors on port
lerobot-setup-motors-selective \
    --robot.type=so100_follower \
    --robot.port=/dev/ttyUSB0 \
    --scan-only
```
"""

from dataclasses import dataclass, field

import draccus

from lerobot.robots import (  # noqa: F401
    RobotConfig,
    koch_follower,
    lekiwi,
    make_robot_from_config,
    so100_follower,
    so101_follower,
)
from lerobot.teleoperators import (  # noqa: F401
    TeleoperatorConfig,
    koch_leader,
    make_teleoperator_from_config,
    so100_leader,
    so101_leader,
)

COMPATIBLE_DEVICES = [
    "koch_follower",
    "koch_leader",
    "so100_follower",
    "so100_leader",
    "so101_follower",
    "so101_leader",
    "lekiwi",
]


@dataclass
class SetupConfig:
    robot: RobotConfig | None = None
    teleop: TeleoperatorConfig | None = None
    motors: list[str] = field(default_factory=list)
    scan_only: bool = False

    def __post_init__(self):
        if bool(self.teleop) == bool(self.robot):
            raise ValueError("Choose either a teleop or a robot.")

        self.device = self.robot if self.robot else self.teleop


def setup_motors_selective(
    device,
    motors_to_setup: list[str] | None = None,
    scan_only: bool = False,
) -> None:
    """
    Set up motors with selective control.

    Args:
        device: Robot or Teleoperator instance
        motors_to_setup: List of motor names or IDs to set up. If None, prompt user for each motor.
        scan_only: If True, only scan and report motors found.
    """
    if not hasattr(device, "bus"):
        raise ValueError(f"{device} does not have a motor bus.")

    bus = device.bus

    print("\n" + "=" * 60)
    print(f"Motor Setup for {device}")
    print("=" * 60)
    print(f"Available motors in config: {list(bus.motors.keys())}")
    print()

    if scan_only:
        print("Scanning for motors on the port...")
        if not bus.is_connected:
            bus._connect(handshake=False)

        # Scan common baudrates
        print(f"Scanning baudrates: {bus.available_baudrates}")
        found_motors = {}
        for baudrate in bus.available_baudrates:
            bus.set_baudrate(baudrate)
            ids_models = bus.broadcast_ping()
            if ids_models:
                found_motors[baudrate] = ids_models
                print(f"  Baudrate {baudrate}: Found IDs {list(ids_models.keys())}")

        if not found_motors:
            print("No motors found on the port.")
        bus.port_handler.closePort()
        return

    # Determine which motors to set up
    if motors_to_setup is None:
        motors_to_setup = []

    if motors_to_setup:
        # Build mapping from motor ID to motor name
        id_to_name = {}
        for name, motor in bus.motors.items():
            motor_id = motor.id if hasattr(motor, "id") else None
            if motor_id is not None:
                id_to_name[str(motor_id)] = name

        # Validate and convert specified motors (can be names or IDs)
        valid_motors = set(bus.motors.keys())
        converted_motors = []
        for motor_spec in motors_to_setup:
            # Check if it's a motor name
            if motor_spec in valid_motors:
                converted_motors.append(motor_spec)
            # Check if it's a motor ID
            elif motor_spec in id_to_name:
                converted_motors.append(id_to_name[motor_spec])
            else:
                raise ValueError(
                    f"Motor '{motor_spec}' not found. Available motors (names): {list(valid_motors)} or (IDs): {list(id_to_name.keys())}"
                )
        motors_list = converted_motors
    else:
        # Interactive mode: prompt for each motor
        motors_list = list(reversed(bus.motors.keys()))

    print(f"Motors to configure: {motors_list}\n")

    for motor in motors_list:
        if motors_to_setup:
            # Non-interactive mode: just set up the specified motors
            print(f"\nSetting up '{motor}' motor...")
            input("Connect the controller board to the motor and press Enter.")
            bus.setup_motor(motor)
            print(f"✓ '{motor}' motor ID set to {bus.motors[motor].id}")
        else:
            # Interactive mode: allow skipping
            print(f"\nConfigure '{motor}' motor?")
            response = input("(y)es / (s)kip / (q)uit? [y/s/q]: ").strip().lower()

            if response == "q":
                print("Setup cancelled.")
                return
            elif response == "s":
                print(f"Skipping '{motor}'")
                continue
            elif response in ("y", ""):
                print(f"Setting up '{motor}'...")
                input("Connect the controller board to the motor and press Enter.")
                try:
                    bus.setup_motor(motor)
                    print(f"✓ '{motor}' motor ID set to {bus.motors[motor].id}")
                except Exception as e:
                    print(f"✗ Error setting up '{motor}': {e}")
                    retry = input("Retry this motor? (y/n): ").strip().lower()
                    if retry == "y":
                        bus.setup_motor(motor)
                        print(f"✓ '{motor}' motor ID set to {bus.motors[motor].id}")
            else:
                print("Invalid input. Please enter 'y', 's', or 'q'.")

    print("\n" + "=" * 60)
    print("Motor setup complete!")
    print("=" * 60)


@draccus.wrap()
def setup_motors(cfg: SetupConfig):
    if cfg.device.type not in COMPATIBLE_DEVICES:
        raise NotImplementedError(f"Device type '{cfg.device.type}' is not supported.")

    if isinstance(cfg.device, RobotConfig):
        device = make_robot_from_config(cfg.device)
    else:
        device = make_teleoperator_from_config(cfg.device)

    motors_to_setup = cfg.motors if cfg.motors else None
    setup_motors_selective(device, motors_to_setup=motors_to_setup, scan_only=cfg.scan_only)


def main():
    setup_motors()


if __name__ == "__main__":
    main()
