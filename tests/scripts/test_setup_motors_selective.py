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

import pytest

from lerobot.scripts.lerobot_setup_motors_selective import SetupConfig


def test_setup_config_requires_device():
    """Test that SetupConfig requires either robot or teleop."""
    with pytest.raises(ValueError, match="Choose either a teleop or a robot"):
        SetupConfig()

    with pytest.raises(ValueError, match="Choose either a teleop or a robot"):
        SetupConfig(robot=None, teleop=None)


def test_setup_config_both_devices_not_allowed():
    """Test that SetupConfig doesn't allow both robot and teleop."""
    from lerobot.robots import so100_follower
    from lerobot.teleoperators import so100_leader

    robot_cfg = so100_follower.SO100FollowerConfig()
    teleop_cfg = so100_leader.SO100LeaderConfig()

    with pytest.raises(ValueError, match="Choose either a teleop or a robot"):
        SetupConfig(robot=robot_cfg, teleop=teleop_cfg)


def test_setup_config_robot_only():
    """Test that SetupConfig accepts robot-only config."""
    from lerobot.robots import so100_follower

    robot_cfg = so100_follower.SO100FollowerConfig()
    cfg = SetupConfig(robot=robot_cfg)
    assert cfg.device == robot_cfg
    assert cfg.robot == robot_cfg


def test_setup_config_teleop_only():
    """Test that SetupConfig accepts teleop-only config."""
    from lerobot.teleoperators import so100_leader

    teleop_cfg = so100_leader.SO100LeaderConfig()
    cfg = SetupConfig(teleop=teleop_cfg)
    assert cfg.device == teleop_cfg
    assert cfg.teleop == teleop_cfg


def test_setup_config_motors_list():
    """Test that motors can be specified as a list."""
    from lerobot.robots import so100_follower

    robot_cfg = so100_follower.SO100FollowerConfig()
    cfg = SetupConfig(robot=robot_cfg, motors=["shoulder", "elbow"])
    assert cfg.motors == ["shoulder", "elbow"]


def test_setup_config_scan_only():
    """Test that scan_only flag is properly set."""
    from lerobot.robots import so100_follower

    robot_cfg = so100_follower.SO100FollowerConfig()
    cfg = SetupConfig(robot=robot_cfg, scan_only=True)
    assert cfg.scan_only is True
