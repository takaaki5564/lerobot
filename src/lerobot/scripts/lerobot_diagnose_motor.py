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
Diagnostic tool to test if a motor is functioning correctly.

This script connects to a single motor and tests:
1. Basic communication (ping)
2. All supported baud rates
3. Motor ID and model number
4. Basic register read operations

Examples:

```shell
# Test motor ID 6
lerobot-diagnose-motor \
    --robot.type=lekiwi \
    --robot.port=/dev/ttyACM0 \
    --motor_id=6

# Test with specific baud rate
lerobot-diagnose-motor \
    --robot.type=lekiwi \
    --robot.port=/dev/ttyACM0 \
    --motor_id=6 \
    --baudrate=1000000
```
"""

from dataclasses import dataclass

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
class DiagnoseConfig:
    robot: RobotConfig | None = None
    teleop: TeleoperatorConfig | None = None
    motor_id: int | None = None
    baudrate: int | None = None

    def __post_init__(self):
        if bool(self.teleop) == bool(self.robot):
            raise ValueError("Choose either a teleop or a robot.")

        self.device = self.robot if self.robot else self.teleop


def diagnose_motor(device, motor_id: int, baudrate: int | None = None) -> None:
    """
    Diagnose a single motor by testing communication.

    Args:
        device: Robot or Teleoperator instance
        motor_id: Motor ID to test
        baudrate: Specific baud rate to test (None = try all)
    """
    if not hasattr(device, "bus"):
        raise ValueError(f"{device} does not have a motor bus.")

    bus = device.bus

    print("\n" + "=" * 70)
    print(f"Motor Diagnostic Tool for {device}")
    print("=" * 70)
    print(f"Testing motor ID: {motor_id}")
    print()

    # If specific baudrate, test only that
    baudrates_to_test = [baudrate] if baudrate else bus.available_baudrates

    found = False
    for br in baudrates_to_test:
        print(f"Testing baudrate {br}...", end=" ", flush=True)

        try:
            if not bus.is_connected:
                bus._connect(handshake=False)

            bus.set_baudrate(br)

            # Try to ping the motor
            model_number = bus.ping(motor_id, num_retry=2, raise_on_error=False)

            if model_number is not None:
                print(f"✓ SUCCESS")
                print(f"  Motor ID: {motor_id}")
                print(f"  Model Number: {model_number}")
                print(f"  Baud Rate: {br}")

                # Try to read some registers
                try:
                    # Read motor ID from register (register 0 for most motors)
                    if hasattr(bus, "read_register"):
                        reg_id = bus.read_register(motor_id, "id")
                        print(f"  Register ID: {reg_id}")
                except Exception as e:
                    print(f"  Register read failed: {e}")

                found = True
                print()
            else:
                print("✗ No response")

        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            if bus.is_connected:
                try:
                    bus.port_handler.closePort()
                except Exception:
                    pass

    if not found:
        print("\n" + "=" * 70)
        print(f"RESULT: Motor ID {motor_id} did NOT respond on any tested baud rate.")
        print("=" * 70)
        print("\nPossible issues:")
        print("1. Motor is not powered")
        print("2. Motor is not physically connected to the port")
        print("3. Motor ID is incorrect (use --scan_only to find actual IDs)")
        print("4. Motor is faulty/damaged")
        print("5. Serial port is not accessible")
        print()
    else:
        print("=" * 70)
        print(f"RESULT: Motor ID {motor_id} is responding correctly!")
        print("=" * 70)
        print()


@draccus.wrap()
def diagnose(cfg: DiagnoseConfig):
    if cfg.motor_id is None:
        raise ValueError("--motor_id is required. Specify which motor to test (e.g., --motor_id=6)")

    if cfg.device.type not in COMPATIBLE_DEVICES:
        raise NotImplementedError(f"Device type '{cfg.device.type}' is not supported.")

    if isinstance(cfg.device, RobotConfig):
        device = make_robot_from_config(cfg.device)
    else:
        device = make_teleoperator_from_config(cfg.device)

    diagnose_motor(device, motor_id=cfg.motor_id, baudrate=cfg.baudrate)


def main():
    diagnose()


if __name__ == "__main__":
    main()
