# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

LeRobot is a state-of-the-art machine learning library for real-world robotics developed by Hugging Face. It provides pre-trained models, datasets, simulation environments, and tools for training and deploying robotic control policies using imitation learning and reinforcement learning.

## Key Commands

### Development Setup
```bash
# Install with all optional dependencies
pip install -e ".[dev]"

# Install specific feature groups
pip install -e ".[test]"  # Testing dependencies
pip install -e ".[rl]"    # RL environments
pip install -e ".[grpc]"  # gRPC for distributed inference
```

### Code Quality
```bash
# Run linting and auto-fix issues
ruff check --fix .
ruff format .

# Type checking (partially enabled for envs module)
mypy src/lerobot

# Security checks
bandit -r src/lerobot -c pyproject.toml

# Pre-commit hooks (if installed)
pre-commit run --all-files
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_datasets.py

# Run with coverage
pytest --cov=lerobot

# End-to-end tests (via Makefile)
make test-end-to-end DEVICE=cpu  # or cuda
make test-act-ete-train DEVICE=cpu
make test-diffusion-ete-eval DEVICE=cpu
```

### Training and Evaluation
```bash
# Train a policy
lerobot-train \
    --policy.type=act \
    --env.type=aloha \
    --dataset.repo_id=lerobot/aloha_sim_transfer_cube_human

# Resume training from checkpoint
lerobot-train \
    --config_path=outputs/train/checkpoints/000002/pretrained_model/train_config.json \
    --resume=true

# Evaluate a policy
lerobot-eval \
    --policy.path=outputs/train/checkpoints/latest/pretrained_model \
    --env.type=aloha

# Visualize dataset
lerobot-dataset-viz --dataset.repo_id=lerobot/pusht
```

### Hardware and Recording
```bash
# Calibrate robot
lerobot-calibrate --robot-type=so100

# Find serial ports
lerobot-find-port

# Record episodes
lerobot-record \
    --robot-type=so100 \
    --fps=30 \
    --root=data \
    --repo-id=my_dataset
```

## Architecture

### Policy Structure
All policies inherit from `PreTrainedPolicy` and follow this pattern:
- Configuration class (e.g., `ACTConfig`) in `lerobot/configs/policies/`
- Policy implementation in `lerobot/policies/{policy_name}/`
- Processor for data preprocessing
- Integration with HuggingFace model hub

### Key Directories
- `src/lerobot/policies/`: Policy implementations (ACT, Diffusion, TDMPC, VQ-BeT, SmolVLA, Pi0)
- `src/lerobot/envs/`: Environment wrappers with gym interface
- `src/lerobot/datasets/`: Dataset handling and LeRobotDataset format
- `src/lerobot/robots/`: Hardware robot implementations
- `src/lerobot/cameras/`: Camera drivers (OpenCV, RealSense)
- `src/lerobot/motors/`: Motor controllers (Dynamixel, Feetech)

### Dataset Format
LeRobotDataset uses:
- Parquet files for episode metadata
- Video compression for images
- Temporal delta encoding for efficient querying
- HuggingFace hub integration

### Configuration System
Uses DrAccus for hierarchical configuration:
- Base configs in `src/lerobot/configs/`
- Override via CLI arguments or JSON files
- Policy-specific configurations

## Development Guidelines

### Adding New Policies
1. Create directory under `src/lerobot/policies/`
2. Implement policy class inheriting from `PreTrainedPolicy`
3. Add configuration class in `src/lerobot/configs/policies/`
4. Add tests in `tests/policies/`
5. Update factory in `src/lerobot/policies/__init__.py`

### Working with Hardware
- Abstract base classes in `src/lerobot/robots/`, `src/lerobot/cameras/`, `src/lerobot/motors/`
- Mock implementations available for testing
- Teleoperation interfaces in `src/lerobot/teleoperators/`

### Testing Strategy
- Unit tests with fixtures in `tests/`
- Hardware mocking for CI/CD
- End-to-end tests in Makefile
- Policy-specific test configurations

### Performance Considerations
- Multi-GPU training supported via `accelerate`
- Async inference with gRPC
- Video compression for efficient storage
- Batch processing optimizations