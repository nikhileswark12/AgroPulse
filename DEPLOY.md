# AgroPulse Deployment Guide

## Prerequisites
- Docker and Docker Compose installed
- Make installed

## Setup
1. Initialize the environment configuration:
   ```bash
   make setup
   ```
2. Edit `.env` and fill in the required variables (especially `SECRET_KEY`, `MONGO_URI`, and email settings).

## Build
Build the Docker image:
```bash
make build
```

## Run
Start the application stack (web, MongoDB, Redis) in the background:
```bash
make up
```

## Health Check
Verify the application is running:
```bash
make health
```

## Retraining the Model
To retrain the machine learning model, run the training script:
```bash
python ml/train_model.py
```
This will update the `trained_model.pkl` and encoders in the `ml/` directory. Be sure to rebuild or restart the container to pick up changes.
