# AWS Getting Started Guide for Educational Video Generator

This guide walks you through setting up AWS from scratch and deploying the backend.

## 📋 Prerequisites

- Credit/Debit card (AWS requires this, but Free Tier covers most usage)
- Email address
- Phone number for verification

---

## Step 1: Create AWS Account

1. Go to [aws.amazon.com](https://aws.amazon.com/)
2. Click **"Create an AWS Account"**
3. Enter email and choose account name
4. Verify email and set root password
5. Enter contact information (choose "Personal" for personal projects)
6. Enter payment method (won't be charged for Free Tier usage)
7. Verify phone number
8. Choose **"Basic Support - Free"** plan
9. Complete sign-up

⏱️ Takes about 10-15 minutes. Account activation can take up to 24 hours (usually instant).

---

## Step 2: Secure Your Account (Important!)

1. Sign in to [AWS Console](https://console.aws.amazon.com/)
2. Search for **"IAM"** in the top search bar
3. Click **"Users"** → **"Create user"**
4. Username: `edugen-admin`
5. Check **"Provide user access to AWS Management Console"**
6. Choose **"I want to create an IAM user"**
7. Set a password
8. Click **"Next"**
9. Select **"Attach policies directly"**
10. Check these policies:
    - `AmazonEC2FullAccess`
    - `AmazonS3FullAccess`
    - `IAMUserChangePassword`
11. Click **"Next"** → **"Create user"**
12. **Download the credentials CSV** - you'll need these!

---

## Step 3: Create Key Pair for SSH

1. Go to **EC2** service (search in top bar)
2. In left sidebar, click **"Key Pairs"** (under Network & Security)
3. Click **"Create key pair"**
4. Name: `edugen-key`
5. Key pair type: **RSA**
6. Key file format: **.pem** (for OpenSSH)
7. Click **"Create key pair"**
8. **Save the downloaded `edugen-key.pem` file** - you need this to SSH!

⚠️ Keep this file safe! If lost, you cannot recover it.

---

## Step 4: Launch EC2 Instance

1. Go to **EC2** → **"Instances"** → **"Launch instances"**

2. **Name:** `edugen-server`

3. **Application and OS Image:**
   - Click **"Ubuntu"**
   - Select **Ubuntu Server 22.04 LTS (HVM)** - Free tier eligible
   - Architecture: **64-bit (x86)**

4. **Instance type:**
   - For testing: `t2.micro` (Free Tier - 1 vCPU, 1GB RAM)
   - For production: `t3.medium` (2 vCPU, 4GB RAM) - ~$30/month
   - **Recommended for video generation:** `t3.large` (2 vCPU, 8GB RAM) - ~$60/month

5. **Key pair:** Select `edugen-key` (created in Step 3)

6. **Network settings:** Click **"Edit"**
   - Auto-assign Public IP: **Enable**
   - Create security group: **Create security group**
   - Security group name: `edugen-sg`
   - Description: `Educational Video Generator`
   - **Add these rules:**
   
   | Type | Port Range | Source | Description |
   |------|------------|--------|-------------|
   | SSH | 22 | My IP | SSH access |
   | Custom TCP | 8000 | Anywhere (0.0.0.0/0) | API access |
   | HTTP | 80 | Anywhere (0.0.0.0/0) | Web access |
   | HTTPS | 443 | Anywhere (0.0.0.0/0) | Secure web |

7. **Configure storage:**
   - Size: **30 GB** (Free tier allows up to 30GB)
   - Volume type: **gp3**

8. Click **"Launch instance"**

---

## Step 5: Connect to Your Instance

### Wait for Instance to Start
1. Go to **EC2** → **"Instances"**
2. Wait until **Instance State** shows **"Running"** (green)
3. Copy the **Public IPv4 address** (e.g., `54.123.45.67`)

### Connect via SSH

**On Windows (PowerShell):**

First, move your key file to a secure location:
```powershell
# Create .ssh folder if not exists
mkdir -Force $HOME\.ssh

# Move key file
Move-Item "C:\Users\Mahak\Downloads\edugen-key.pem" "$HOME\.ssh\edugen-key.pem"

# Windows doesn't need chmod, but for WSL users:
# chmod 400 ~/.ssh/edugen-key.pem
```

Connect:
```powershell
ssh -i "$HOME\.ssh\edugen-key.pem" ubuntu@YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with your instance's IP address.

---

## Step 6: Deploy the Application

Once connected via SSH, run these commands:

### Option A: Quick Setup (Recommended)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Clone your repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/devForge.git
cd devForge

# Run the setup script
chmod +x deploy/setup_ec2.sh
sudo ./deploy/setup_ec2.sh
```

### Option B: Manual Setup

If you don't have a GitHub repo yet, upload files directly:

**From your local PowerShell (not SSH):**
```powershell
# Create a zip of the project
Compress-Archive -Path "C:\Users\Mahak\devForge\*" -DestinationPath "C:\Users\Mahak\devForge.zip" -Force

# Upload to EC2
scp -i "$HOME\.ssh\edugen-key.pem" "C:\Users\Mahak\devForge.zip" ubuntu@YOUR_PUBLIC_IP:~/
```

**Then on EC2 (SSH):**
```bash
# Install unzip
sudo apt update && sudo apt install -y unzip

# Extract
unzip devForge.zip -d devForge
cd devForge

# Run setup
chmod +x deploy/setup_ec2.sh
sudo ./deploy/setup_ec2.sh
```

---

## Step 7: Configure Environment Variables

After setup completes:

```bash
# Edit the environment file
sudo nano /opt/edugen/.env
```

Add these lines:
```
CORS_ORIGINS=https://your-vercel-app.vercel.app
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

Save with `Ctrl+O`, `Enter`, `Ctrl+X`

Restart the service:
```bash
sudo systemctl restart edugen
```

---

## Step 8: Create S3 Bucket for Videos

1. Go to **S3** service in AWS Console
2. Click **"Create bucket"**
3. **Bucket name:** `edugen-videos-YOURNAME` (must be globally unique)
4. **Region:** Same as your EC2 (e.g., `us-east-1`)
5. **Object Ownership:** ACLs disabled (recommended)
6. **Block Public Access:** Uncheck "Block all public access" 
   - Check the acknowledgment box
7. Click **"Create bucket"**

### Set Bucket Policy (for public video access)
1. Click your bucket name
2. Go to **"Permissions"** tab
3. Scroll to **"Bucket policy"** → **"Edit"**
4. Paste this policy (replace `YOUR-BUCKET-NAME`):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

5. Click **"Save changes"**

---

## Step 9: Create Access Keys for S3

1. Go to **IAM** → **Users** → **edugen-admin**
2. Click **"Security credentials"** tab
3. Scroll to **"Access keys"** → **"Create access key"**
4. Select **"Application running outside AWS"**
5. Click **"Next"** → **"Create access key"**
6. **Download the CSV file** or copy both:
   - Access key ID
   - Secret access key

⚠️ This is the only time you can view the secret key!

Update your EC2 environment with these keys (Step 7).

---

## Step 10: Verify Deployment

Test the API:
```bash
# On EC2
curl http://localhost:8000/api/health

# From your local machine (replace with your EC2 IP)
curl http://YOUR_EC2_IP:8000/api/health
```

Expected response:
```json
{"status": "healthy", "ollama_available": true}
```

---

## Step 11: Set Up Elastic IP (Optional but Recommended)

By default, EC2 public IP changes when you stop/start the instance.
To get a permanent IP:

1. Go to **EC2** → **"Elastic IPs"** (under Network & Security)
2. Click **"Allocate Elastic IP address"**
3. Click **"Allocate"**
4. Select the new IP → **"Actions"** → **"Associate Elastic IP address"**
5. Select your `edugen-server` instance
6. Click **"Associate"**

Now this IP stays the same forever!

---

## 📊 Cost Estimate (Monthly)

| Resource | Free Tier | After Free Tier |
|----------|-----------|-----------------|
| t2.micro EC2 | 750 hrs/month FREE | ~$8/month |
| t3.medium EC2 | - | ~$30/month |
| t3.large EC2 | - | ~$60/month |
| 30GB EBS Storage | 30GB FREE | ~$2.40/month |
| S3 Storage | 5GB FREE | $0.023/GB |
| Data Transfer Out | 100GB FREE | $0.09/GB |
| Elastic IP (if running) | FREE | FREE |
| Elastic IP (if stopped) | - | $0.005/hr |

**First Year Total (t2.micro):** FREE under Free Tier  
**Production (t3.large):** ~$65-80/month

---

## 🆘 Troubleshooting

### Can't SSH to instance
- Check security group has SSH (port 22) open for your IP
- Verify key file path is correct
- Make sure instance is running

### API not responding
```bash
# Check service status
sudo systemctl status edugen

# View logs
sudo journalctl -u edugen -f

# Restart service
sudo systemctl restart edugen
```

### Ollama not running
```bash
# Check Ollama status
sudo systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Pull model manually
ollama pull phi3:mini
```

### Out of memory
- Upgrade to t3.medium or t3.large
- Or add swap space:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 🎉 Next Steps

After backend is deployed:

1. **Deploy Frontend to Vercel:**
   - Push code to GitHub
   - Import to Vercel
   - Set `VITE_API_URL=http://YOUR_EC2_IP:8000`

2. **Set up custom domain (optional):**
   - Buy domain (Namecheap, GoDaddy, etc.)
   - Point to Elastic IP
   - Add SSL with Let's Encrypt

3. **Monitor your app:**
   - Check CloudWatch metrics in AWS Console
   - Set up billing alerts

---

## Quick Reference

| Item | Value |
|------|-------|
| SSH Command | `ssh -i ~/.ssh/edugen-key.pem ubuntu@YOUR_IP` |
| App Directory | `/opt/edugen` |
| Config File | `/opt/edugen/.env` |
| Service Name | `edugen` |
| View Logs | `sudo journalctl -u edugen -f` |
| Restart App | `sudo systemctl restart edugen` |
| Restart Ollama | `sudo systemctl restart ollama` |
| API URL | `http://YOUR_IP:8000/api/` |
