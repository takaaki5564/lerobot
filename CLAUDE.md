# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

LeRobot is Hugging Face's PyTorch library for real-world robotics: hardware-agnostic robot/teleop interfaces, the `LeRobotDataset` format (Parquet + MP4) hosted on the HF Hub, and SoTA policies (imitation learning, RL, VLAs). Python 3.12+, `src/`-layout package, distributed via PyPI as `lerobot`. It provides pre-trained models, datasets, simulation environments, and tools for training and deploying robotic control policies.

## Common commands

The repo uses `uv` if available; CI uses `uv sync --extra <extra>` to install. Most CLI tools are installed as console scripts via `[project.scripts]` (see `pyproject.toml`).

Run tests:
```bash
pytest -sv tests                       # full unit tests (CI: uv run pytest tests -vv --maxfail=10)
pytest -sv tests/datasets/test_datasets.py::test_factory   # single test
make test-end-to-end                   # end-to-end policy train+eval cycles (also: test-act-ete-train, test-diffusion-ete-eval, etc.)
make DEVICE=cuda test-end-to-end       # override device (defaults to cpu)
```

Test artifacts live in `tests/artifacts/` and require `git lfs install && git lfs pull`. `tests/conftest.py` registers fixture plugins from `tests/fixtures/` (dataset_factories, files, hub, optimizers).

Lint / format:
```bash
pre-commit install                     # one-time
pre-commit run --all-files             # ruff-format, ruff (--fix), typos, pyupgrade --py312-plus
```
Ruff target is `py312`, line length 110. `__init__.py` files are excluded from `F401`/`F403`. The `src/lerobot/policies/wall_x/**` tree has many naming/style rules disabled because it tracks upstream Qwen2_5_VL.

Train / eval / record (console scripts):
```bash
lerobot-train --policy=act --dataset.repo_id=lerobot/aloha_mobile_cabinet
lerobot-eval --policy.path=<path-or-hub-id> --env.type=libero --env.task=libero_object --eval.n_episodes=10
lerobot-record / lerobot-replay / lerobot-teleoperate / lerobot-calibrate
lerobot-info                           # prints installed extras + versions
```
All scripts above are dispatched via `lerobot.scripts.lerobot_*:main`. See `pyproject.toml` `[project.scripts]` for the full list.

Docker:
```bash
make build-user        # docker/Dockerfile.user (consumer image)
make build-internal    # docker/Dockerfile.internal (CI/GPU image: huggingface/lerobot-gpu)
```

## Configuration system (draccus + parser.wrap)

`@parser.wrap()` from `src/lerobot/configs/parser.py` decorates the `train` / `eval` entry points. It builds a draccus config tree (e.g. `TrainPipelineConfig` in `configs/train.py`) from CLI args and supports two important extra mechanisms:

- **Nested dot-notation overrides**: `--policy.dim_model=64`, `--dataset.image_transforms.enable=true`, `--env.episode_length=5`. `get_cli_overrides("policy")` re-extracts these to forward into a nested config when needed.
- **Pretrained-path loading**: `--policy.path=<dir-or-hub>` (or `--config_path=<train_config.json>` for `--resume=true`) reads a saved `train_config.json` / pretrained config, then re-applies CLI overrides on top. This is why `TrainPipelineConfig.validate()` parses `sys.argv` a second time.
- **Plugin discovery**: `lerobot.utils.import_utils.register_third_party_plugins()` is called at the top of `train`/`eval` to import out-of-tree packages that register additional policies/envs/robots into draccus' `ChoiceRegistry`.

Configs are persisted as JSON next to checkpoints (see `lerobot/utils/hub.HubMixin`) and are restorable via `from_pretrained`.

## Architecture map

The library is organized around a small set of hot-pluggable abstractions, each with a `factory.py`:

- **`policies/`** — `PreTrainedPolicy` (`policies/pretrained.py`) extends `nn.Module + HubMixin`. Each policy lives in a subpackage with `configuration_<name>.py` + `modeling_<name>.py`. `make_policy` and `make_pre_post_processors` are in `policies/factory.py`. Subclasses must define `config_class` + `name` (enforced in `__init_subclass__`). Available policy types include `act`, `diffusion`, `tdmpc`, `vqbet`, `pi0`, `pi05`, `pi0_fast`, `smolvla`, `groot`, `multi_task_dit`, `sac`, `sarm`, `wall_x`, `xvla`, plus `rtc`. New VLA-class policies usually require the `transformers-dep` extra (pinned to `transformers==5.3.0`).
- **`processor/`** — `ProcessorStep` + `DataProcessorPipeline` (`processor/pipeline.py`). Pipelines are the canonical way to transform `EnvTransition` dicts (observation/action/reward/done/info/complementary_data — see `lerobot/types.py`). Pre/post-processors are *separate* pipelines saved alongside policies (normalize, device move, rename, tokenize, relative↔absolute action conversion, gym/env adapters, …) and reconstructed via the `ProcessorStepRegistry`. `_reconnect_relative_absolute_steps` in `policies/factory.py` is an example of post-deserialization wiring that some steps require.
- **`datasets/`** — `LeRobotDataset` (`datasets/lerobot_dataset.py`) is the core dataset class; metadata, stats, sampler, video decoding, streaming variants, and dataset-editing tools (`dataset_tools.py`, `aggregate.py`, `multi_dataset.py`) all live here. v2.1 → v3.0 migration is in `scripts/convert_dataset_v21_to_v30.py`. Uses Parquet files for episode metadata and video compression for efficient storage.
- **`robots/` and `teleoperators/`** — both inherit from abstract base classes (`robots/robot.py`, `teleoperators/teleoperator.py`) with `connect / disconnect / get_observation / send_action` (and `get_action` for teleops). Calibration is loaded automatically from `HF_LEROBOT_CALIBRATION`. Each device has a subpackage; bimanual variants are composed (`bi_so_follower`, `bi_openarm_follower`, …).
- **`cameras/` and `motors/`** — analogous abstractions for sensor/actuator hardware (`opencv`, `realsense`, `reachy2_camera`, `zmq` cameras; `dynamixel`, `feetech`, `damiao`, `robstride` motor buses).
- **`envs/`** — Gymnasium env wrappers + factories. Currently registered: `aloha`, `pusht`, `libero`, `metaworld` (each behind its own extra). `make_env` and `make_env_pre_post_processors` are in `envs/factory.py`.
- **`rl/`** — HIL-SERL / SAC training loop pieces: `actor.py`, `learner.py`, `learner_service.py`, replay `buffer.py`/`queue.py`, `gym_manipulator.py`, plus `wandb_utils.py` (used by `lerobot_train` too). Multi-GPU training supported via `accelerate`.
- **`async_inference/` + `transport/`** — gRPC-based remote inference (`policy_server.py` ↔ `robot_client.py`). The proto is `transport/services.proto`; generated stubs (`*_pb2.py`, `*_pb2_grpc.py`) are checked in and excluded from ruff. Regenerate via `grpcio-tools` (in the `dev` extra).
- **`scripts/`** — every CLI entry point. Note that `__init__.py` re-exports availability lists (`available_policies`, `available_robots`, …) used both by tests (`tests/test_available.py`) and `lerobot-info`; update it when adding a new policy/robot/env.

## Extras and dependencies

`pyproject.toml` defines a large matrix of optional extras (per-policy, per-robot, per-sim, plus `dev`, `test`, `all`). Common patterns:
- Hardware extras: `feetech`, `dynamixel`, `damiao`, `robstride`, `gamepad`, `hopejr`, `lekiwi`, `openarms`, `reachy2`, `unitree_g1`, `intelrealsense`, `phone`, `kinematics`.
- Policy extras: `pi`, `pi05`, `smolvla`, `groot`, `wallx`, `xvla`, `multi_task_dit`, `sarm`, `hilserl` — most depend on the umbrella `transformers-dep` extra (pinned to `transformers==5.3.0`).
- Sim extras: `aloha`, `pusht`, `libero` (Linux-only), `metaworld`.
- `all` deliberately omits `groot` and `unitree_g1` (special install instructions for `flash-attn` / `unitree_sdk2`).

mypy is configured per-module in `pyproject.toml`. Strictness is being rolled out gradually; today only `lerobot.envs.*`, `lerobot.configs.*`, `lerobot.optim.*`, `lerobot.model.*`, `lerobot.cameras.*`, `lerobot.motors.*`, and `lerobot.transport.*` are checked. When adding new modules, follow the existing override pattern rather than enabling repo-wide.

## Tests layout

Mirrors the package: `tests/datasets/`, `tests/policies/`, `tests/cameras/`, `tests/motors/`, `tests/robots/`, `tests/teleoperators/`, `tests/envs/`, etc. `tests/mocks/` holds fakes (notably `mock_serial`-based motor mocks — `mock-serial` is in the `test` extra). Slow / GPU tests run via the `Full Tests` workflow (triggered on PR review-approved or push-to-main) and the GPU container; `Fast Tests` runs on every PR.

## Conventions worth knowing

- **`name` class attribute is mandatory** for `Robot`, `Teleoperator`, and `PreTrainedPolicy` subclasses; it's the registry key used by draccus and `available_*` lists.
- **`from_pretrained` / `_save_pretrained` everywhere** — policies, configs, processors, and `TrainPipelineConfig` all subclass `HubMixin` (`lerobot/utils/hub.py`) for HF Hub round-trips; saved state is `safetensors` + JSON config(s).
- **Don't import heavyweight deps at package import time.** `lerobot/__init__.py` keeps a pure-Python availability index so that `import lerobot` stays cheap; pull from sibling factories/configs lazily.
- **Train resume**: `--resume=true` requires `--config_path=<…/train_config.json>`. The config is restored from disk first, then CLI overrides apply.
- **AI policy** (`AI_POLICY.md`): contributors are asked to disclose substantial AI assistance in PRs and to vet generated code before submitting.

## Development Guidelines

### Adding New Policies
1. Create directory under `src/lerobot/policies/{policy_name}/`
2. Implement policy class inheriting from `PreTrainedPolicy` in `modeling_{policy_name}.py`
3. Add configuration class in `configuration_{policy_name}.py`
4. Define `name` and `config_class` class attributes (enforced via `__init_subclass__`)
5. Add tests in `tests/policies/`
6. Update `lerobot/__init__.py` availability lists if needed
7. Register in draccus' `ChoiceRegistry` via factory if applicable

### Working with Hardware
- Abstract base classes: `src/lerobot/robots/robot.py`, `src/lerobot/cameras/camera.py`, `src/lerobot/motors/motors_bus.py`
- Mock implementations available in `tests/mocks/` for testing
- Teleoperation interfaces in `src/lerobot/teleoperators/teleoperator.py`
- Calibration auto-loaded from `HF_LEROBOT_CALIBRATION` environment variable or default path
- Each device type (SO-100, LeKiwi, etc.) has its own subpackage with `__init__.py` for easy imports

### Motor Setup
For selective motor configuration with skip functionality:
```bash
# Interactive mode - skip motors you don't need to reconfigure
lerobot-setup-motors-selective --robot.type=so100_follower --robot.port=/dev/ttyUSB0

# Configure only specific motors
lerobot-setup-motors-selective --robot.type=so100_follower --robot.port=/dev/ttyUSB0 --motors=shoulder,elbow

# Scan for motors on port without configuring
lerobot-setup-motors-selective --robot.type=so100_follower --robot.port=/dev/ttyUSB0 --scan-only
```
See `docs/source/setup_motors_selective.md` for details.

### Testing Strategy
- Unit tests with fixtures in `tests/`; fixture plugins registered in `tests/conftest.py`
- Hardware mocking via `mock-serial` for CI/CD (in `test` extra)
- End-to-end tests in Makefile: `make test-end-to-end DEVICE=cpu|cuda`
- Policy-specific test configurations; artifacts require `git lfs`
- Fast tests run on every PR; full tests run after approval or push to main
