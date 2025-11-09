#!/bin/bash
# Upload recorded dataset to HuggingFace Hub
# Updated for latest LeRobot version

# Check HuggingFace username
if [ -z "$HF_USER" ]; then
    echo "Please set HF_USER environment variable to your HuggingFace username"
    echo "Example: export HF_USER=your_username"
    exit 1
fi

# Dataset configuration
DATASET_NAME="${HF_USER}/lerobot-so100-demo"
LOCAL_DIR="data/${DATASET_NAME}"

echo "Uploading dataset to HuggingFace Hub..."
echo "Repository: $DATASET_NAME"
echo "Local directory: $LOCAL_DIR"
echo ""

# Check if local data exists
if [ ! -d "$LOCAL_DIR" ]; then
    echo "Error: Local data directory not found: $LOCAL_DIR"
    echo "Please record data first using 06_record_data.sh"
    exit 1
fi

# Login to HuggingFace (if not already logged in)
echo "Checking HuggingFace authentication..."
huggingface-cli whoami || huggingface-cli login

# Push dataset to hub
echo "Pushing dataset to HuggingFace Hub..."
# Note: In the latest version, push_to_hub is done during recording
# If you recorded with --dataset.push_to_hub=false, you can manually push using:
python -c "
from lerobot.datasets import LeRobotDataset
from huggingface_hub import HfApi
dataset = LeRobotDataset('$LOCAL_DIR')
api = HfApi()
api.upload_folder(
    folder_path='$LOCAL_DIR',
    repo_id='$DATASET_NAME',
    repo_type='dataset',
    create_pr=False
)
print('Dataset uploaded successfully!')
"

echo ""
echo "Dataset uploaded successfully!"
echo "View your dataset at: https://huggingface.co/datasets/$DATASET_NAME"
echo ""
echo "You can now use this dataset for training in Google Colab"