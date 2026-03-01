# Deployment Guide - Educational Video Generator

## Architecture Overview

```
┌─────────────────────┐         HTTPS          ┌─────────────────────┐
│   React Frontend    │ ◄─────────────────────►│   FastAPI Backend   │
│   (Vercel)          │                        │   (AWS EC2)         │
│                     │                        │                     │
│ yourapp.vercel.app  │   POST /api/generate   │  api.yourdomain.com │
└─────────────────────┘   GET  /api/status     └─────────┬───────────┘
                                                         │
                                            ┌────────────▼────────────┐
                                            │      AWS S3 Bucket      │
                                            │   (Video Storage)       │
                                            └─────────────────────────┘
```

---

## Backend Deployment (AWS EC2)

### Prerequisites
- AWS Account
- EC2 instance (t3.large recommended, 8GB+ RAM for Ollama)
- Ubuntu 22.04 LTS
- S3 bucket for video storage

### Option 1: Automated Setup Script

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Upload the project
scp -i your-key.pem -r ./devForge ubuntu@your-ec2-ip:~/

# Run setup script
cd ~/devForge
sudo bash deploy/setup_ec2.sh
```

### Option 2: Docker Deployment

```bash
# On EC2, install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Run with Docker Compose
cd deploy
docker-compose up -d

# Pull Ollama model
docker exec edugen-ollama ollama pull phi3:mini
```

### Configure Environment

```bash
# Copy and edit .env file
cp .env.example .env
nano .env
```

Required variables:
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=edugen-videos
```

### Verify Deployment

```bash
# Check service status
sudo systemctl status edugen-api
sudo systemctl status ollama

# Test API
curl http://localhost:8000/api/health
```

---

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository

```bash
# Push frontend to GitHub
cd frontend
git init
git add .
git commit -m "Initial frontend"
git remote add origin https://github.com/you/edugen-frontend.git
git push -u origin main
```

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://api.yourdomain.com` |

### Step 4: Update vercel.json

Edit `frontend/vercel.json` and replace `your-ec2-domain.com` with your actual EC2 URL:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.yourdomain.com/api/:path*"
    }
  ]
}
```

---

## S3 Bucket Setup

### Create Bucket

```bash
aws s3 mb s3://edugen-videos --region us-east-1
```

### Configure CORS

Create `cors.json`:
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET"],
      "AllowedOrigins": ["https://yourapp.vercel.app"],
      "ExposeHeaders": []
    }
  ]
}
```

Apply:
```bash
aws s3api put-bucket-cors --bucket edugen-videos --cors-configuration file://cors.json
```

### (Optional) CloudFront CDN

For faster video delivery, set up CloudFront:

1. Create CloudFront distribution
2. Set S3 bucket as origin
3. Update `.env`: `CLOUDFRONT_DOMAIN=d1234567890.cloudfront.net`

---

## SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
```

---

## Monitoring & Logs

```bash
# View API logs
sudo journalctl -u edugen-api -f

# View Ollama logs
sudo journalctl -u ollama -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## Updating the Application

### Backend Updates

```bash
# From your local machine
bash deploy/deploy_backend.sh
```

### Frontend Updates

Push to GitHub - Vercel deploys automatically.

---

## Troubleshooting

### API returns 502 Bad Gateway
```bash
# Check if API is running
sudo systemctl status edugen-api

# Restart if needed
sudo systemctl restart edugen-api
```

### Ollama not responding
```bash
# Check Ollama status
sudo systemctl status ollama

# Check if model is loaded
curl http://localhost:11434/api/tags
```

### Videos not loading
- Check S3 bucket permissions
- Verify CORS configuration
- Check CloudFront distribution status

---

## Cost Estimates

| Resource | Monthly Cost (approx) |
|----------|----------------------|
| EC2 t3.large | $60-80 |
| S3 (10GB) | $0.23 |
| CloudFront | $0.085/GB |
| Vercel (free tier) | $0 |
| **Total** | **~$65-85/month** |

---

## Security Checklist

- [ ] Use SSH key authentication (disable password auth)
- [ ] Configure firewall (ufw) - only allow 80, 443, 22
- [ ] Set up SSL certificate
- [ ] Use IAM roles for S3 access (not root keys)
- [ ] Enable S3 bucket versioning
- [ ] Set up CloudWatch monitoring
- [ ] Regular security updates: `sudo unattended-upgrades`
