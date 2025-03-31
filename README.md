# Hand Gesture Recognition Project

## Project Overview

Real-time hand gesture recognition from short-wave IR images to control/manipulate objects in 3D space.

## Setup

```bash
pip install -r requirements.txt

# Folder Structure
├── data/
│   ├── raw/                     # Original dataset downloaded from Kaggle
│   ├── processed/               # Processed datasets ready for training
│   └── video_samples/           # Sample video frames or videos for testing
│
├── models/                      # Directory to save trained models
│   ├── checkpoints/             # Intermediate training checkpoints
│   └── final/                   # Final model files
│
├── notebooks/                   # Jupyter notebooks for exploration and prototyping
│   └── exploratory_analysis.ipynb
│
├── scripts/                     # Python scripts for training and inference
│   ├── preprocess.py            # Data preprocessing (resizing, normalization)
│   ├── train.py                 # Script to train your model
│   ├── evaluate.py              # Evaluate model performance on validation/test set
│   └── inference.py             # Perform real-time inference from video/webcam
│
├── src/                         # Core project modules
│   ├── dataset.py               # Dataset handling utilities (PyTorch Dataset, TF Dataset, etc.)
│   ├── model.py                 # Model architecture definition
│   ├── utils.py                 # Helper functions (visualization, transformations)
│   └── gesture_control.py       # Logic to map detected gestures to 3D actions
│
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation (setup, usage, commands)
```
