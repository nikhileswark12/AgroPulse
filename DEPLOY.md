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

## Updating Market Data
To update `mandi_prices.csv` with fresh data without manual replacement:
1. Download a new CSV from [AGMARKNET](https://agmarknet.gov.in) manually.
2. Run the update script providing the path to your downloaded CSV:
   ```bash
   make update-data PATH=path/to/new_data.csv
   ```
3. Run the retrain command to train the model on the updated data:
   ```bash
   make retrain
   ```
4. Redeploy with the retrained model:
   ```bash
   make build && make up
   ```

## Deploy to Render
1. Push your code to GitHub
2. Go to https://render.com and create a new Web Service
3. Connect your GitHub repository
4. Render auto-detects render.yaml — click Apply
5. Set the following environment variables manually in the Render dashboard (marked sync: false above):
   - MONGO_URI: your MongoDB Atlas connection string
   - CORS_ORIGINS: https://your-app-name.onrender.com
   - BASE_URL: https://your-app-name.onrender.com
   - MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
   - REDIS_URL: optional, leave blank to use in-memory rate limiting
6. Click Deploy
7. Visit https://your-app-name.onrender.com/health to confirm deployment

## Setup MongoDB Atlas for Production (Free M0 Tier)
1. Create account at https://cloud.mongodb.com
2. Create a free M0 cluster
3. Create a database user with read/write permissions
4. Whitelist 0.0.0.0/0 in Network Access (Render uses dynamic IPs)
5. Get the connection string and set it as MONGO_URI in Render

## Pre-deployment Checklist
- [ ] make test passes locally
- [ ] make health returns model_loaded true locally
- [ ] MONGO_URI points to Atlas, not localhost
- [ ] SECRET_KEY is set to a strong random value
- [ ] CORS_ORIGINS matches the Render app URL exactly
- [ ] BASE_URL matches the Render app URL exactly (used in verification emails)
- [ ] ML model pickle files are committed to the repo OR a build step retrains the model
