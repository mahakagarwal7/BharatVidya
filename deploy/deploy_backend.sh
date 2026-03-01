#!/bin/bash
# deploy/deploy_backend.sh
# Script to deploy backend updates to EC2

set -e

# Configuration
EC2_HOST="ubuntu@your-ec2-ip"
APP_DIR="/opt/edugen"
SSH_KEY="~/.ssh/your-key.pem"

echo "🚀 Deploying Educational Video Generator Backend..."

# Sync code to EC2 (excluding unnecessary files)
echo "📤 Syncing code to EC2..."
rsync -avz --progress \
    -e "ssh -i $SSH_KEY" \
    --exclude 'venv' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude 'node_modules' \
    --exclude 'frontend' \
    --exclude 'outputs' \
    --exclude '.git' \
    --exclude '*.mp4' \
    --exclude '*.pyc' \
    ./ $EC2_HOST:$APP_DIR/

# Install dependencies and restart
echo "🔧 Installing dependencies and restarting service..."
ssh -i $SSH_KEY $EC2_HOST << 'ENDSSH'
cd /opt/edugen
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart edugen-api
echo "✅ Backend deployed and restarted!"
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo "Check status: ssh -i $SSH_KEY $EC2_HOST 'sudo systemctl status edugen-api'"
