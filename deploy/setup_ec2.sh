#!/bin/bash
# deploy/setup_ec2.sh
# AWS EC2 Ubuntu setup script for Educational Video Generator
# Run as: sudo bash setup_ec2.sh

set -e

echo "============================================"
echo "  Educational Video Generator - EC2 Setup"
echo "============================================"

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Python 3.11+
echo "🐍 Installing Python..."
apt-get install -y python3.11 python3.11-venv python3-pip python3.11-dev

# Install system dependencies for MoviePy
echo "🎥 Installing video processing dependencies..."
apt-get install -y ffmpeg libsm6 libxext6 libxrender-dev

# Install Nginx
echo "🌐 Installing Nginx..."
apt-get install -y nginx

# Install Ollama
echo "🧠 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
echo "📥 Pulling phi3:mini model (this may take a while)..."
ollama pull phi3:mini

# Create app directory
echo "📁 Setting up application directory..."
APP_DIR="/opt/edugen"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy your code here
# git clone https://github.com/yourusername/devForge.git .

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create outputs directory
mkdir -p outputs outputs/audio outputs/plans

# Create systemd service for Ollama
echo "⚙️ Creating Ollama service..."
cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama LLM Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for the API
echo "⚙️ Creating EduGen API service..."
cat > /etc/systemd/system/edugen-api.service << 'EOF'
[Unit]
Description=Educational Video Generator API
After=network.target ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/edugen
Environment="PATH=/opt/edugen/venv/bin"
EnvironmentFile=/opt/edugen/.env
ExecStart=/opt/edugen/venv/bin/gunicorn web_app.api:app -w 2 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/edugen << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    # For Let's Encrypt SSL (uncomment after setting up)
    # listen 443 ssl;
    # ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 100M;

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Video files - serve from S3 or local
    location /videos/ {
        alias /opt/edugen/outputs/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/api/health;
    }

    # CORS headers
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type, Authorization";
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/edugen /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

# Create .env template
echo "📝 Creating .env template..."
cat > /opt/edugen/.env.template << 'EOF'
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=edugen-videos

# Optional: CloudFront domain
# CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net

# Ollama
OLLAMA_HOST=http://localhost:11434

# CORS (your frontend URL)
CORS_ORIGINS=https://yourapp.vercel.app,http://localhost:5173
EOF

# Set permissions
chown -R ubuntu:ubuntu /opt/edugen

# Enable and start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama
systemctl enable edugen-api
systemctl start edugen-api
systemctl restart nginx

echo ""
echo "============================================"
echo "  ✅ Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Copy your code to /opt/edugen/"
echo "2. Copy .env.template to .env and fill in values"
echo "3. Run: sudo systemctl restart edugen-api"
echo ""
echo "API will be available at: http://YOUR_EC2_IP/api/"
echo ""
echo "To set up SSL with Let's Encrypt:"
echo "  apt install certbot python3-certbot-nginx"
echo "  certbot --nginx -d yourdomain.com"
