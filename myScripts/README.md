# LeRobot SO-100 Workflow Scripts

This directory contains scripts for the complete LeRobot workflow with SO-100 robot arms, from calibration to training on Google Colab.

## Prerequisites

1. **Environment Setup**:
   ```bash
   conda activate lerobot
   cd ~/work/lerobot
   pip install -e .
   ```

2. **Hardware Requirements**:
   - 2x SO-100 robot arms (leader and follower)
   - USB camera (webcam)
   - USB connections for both arms

3. **HuggingFace Account**:
   ```bash
   export HF_USER=your_huggingface_username
   huggingface-cli login
   ```

## Workflow Steps

### 1. Find Serial Ports
```bash
./01_findport.sh
```
Identifies USB serial ports for your robot arms. Note the ports (typically `/dev/ttyACM0` and `/dev/ttyACM1`).

### 2. Calibrate Robots

**Calibrate Follower Arm** (robot that performs tasks):
```bash
./02_calib_follower.sh
```

**Calibrate Leader Arm** (human control arm):
```bash
./03_calib_leader.sh
```

### 3. Test Teleoperation

**Basic Control Test**:
```bash
./04_remote_ctrl.sh
```

**With Camera Display**:
```bash
./05_camera_data.sh
```

### 4. Record Demonstration Data
```bash
./06_record_data.sh
```

Default settings:
- 5 episodes of 30 seconds each
- 10 seconds reset time between episodes
- Camera recording at 640x480, 30 FPS
- Data saved locally in `data/` directory

### 5. Upload to HuggingFace
```bash
./upload_to_huggingface.sh
```

Uploads your recorded dataset to HuggingFace Hub for training.

### 6. Train on Google Colab

1. Open `train_on_colab.py` in Google Colab
2. Set GPU runtime (Runtime > Change runtime type > GPU)
3. Update configuration with your HF username
4. Run cells sequentially to train your policy

### 7. Replay Episodes (Optional)
```bash
./07_replay.sh [episode_number]
```

Replays recorded episodes on the robot for verification.

## Script Modifications

All scripts use the latest LeRobot CLI commands:
- `lerobot-find-port`: Find USB ports
- `lerobot-calibrate`: Calibrate arms
- `lerobot-teleoperate`: Control robots
- `lerobot-record`: Record demonstrations
- `lerobot-train`: Train policies
- `lerobot-eval`: Evaluate policies

## Common Issues

1. **Permission Denied**: Scripts automatically run `sudo chmod 666` on serial ports
2. **Port Not Found**: Check USB connections and run `./01_findport.sh`
3. **Camera Not Found**: Verify camera index in scripts (default is 0)
4. **HuggingFace Auth**: Run `huggingface-cli login` before uploading

## Customization

### Camera Settings
Edit camera configuration in recording scripts:
```bash
--robot-cameras='{"front": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30}}'
```

### Task Description
Modify task description in `06_record_data.sh`:
```bash
TASK_DESCRIPTION="Your specific task description"
```

### Training Parameters
Adjust hyperparameters in `train_on_colab.py`:
- Batch size
- Learning rate
- Training steps
- Policy type (act, diffusion, tdmpc, vqbet)

## Support

- LeRobot Documentation: https://huggingface.co/docs/lerobot
- GitHub Issues: https://github.com/huggingface/lerobot/issues
- Discord Community: https://discord.gg/s3KuuzsPFb