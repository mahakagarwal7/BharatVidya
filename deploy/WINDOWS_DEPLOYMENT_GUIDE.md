# 🚀 Complete AWS Deployment Guide for Windows

**Time needed**: ~45 minutes  
**Cost**: FREE (using AWS Free Tier)

---

## 📋 What You'll Do

1. Create AWS account
2. Create SSH key
3. Launch a server (EC2)
4. Connect from Windows
5. Upload your code
6. Install everything
7. Deploy frontend

---

# PART 1: CREATE AWS ACCOUNT
*Time: 10-15 minutes*

## Step 1.1: Open AWS Website
```
1. Open Chrome browser
2. Go to: aws.amazon.com
3. Click orange "Create an AWS Account" button (top right)
```

## Step 1.2: Account Details
```
1. Email: Enter your email address
2. Account name: Type "my-video-app"
3. Click "Verify email address"
4. Check your email for 6-digit code
5. Enter the code
6. Click "Verify"
```

## Step 1.3: Set Password
```
1. Create password (needs: uppercase, lowercase, number, symbol)
   Example: MyPassword123!
2. Confirm password (type again)
3. Click "Continue"
```

## Step 1.4: Contact Info
```
1. Select: "Personal - for your own projects"
2. Full Name: Your name
3. Phone: Your phone number
4. Country: Select your country
5. Address: Your address
6. City: Your city
7. State: Your state
8. Postal Code: Your PIN/ZIP
9. ✅ Check the agreement box
10. Click "Continue"
```

## Step 1.5: Payment
```
1. Card Number: Your debit/credit card
2. Expiry: MM/YY
3. CVV: 3 digits on back
4. Cardholder Name: Name on card
5. Click "Verify and Add"

💡 Note: ₹2 verification charge will be refunded
```

## Step 1.6: Phone Verification
```
1. Select "Text message (SMS)"
2. Enter phone number
3. Click "Send SMS"
4. Enter code from SMS
5. Click "Continue"
```

## Step 1.7: Support Plan
```
1. Click "Basic support - Free" (FIRST option)
2. Click "Complete sign up"
3. Wait for "Congratulations" message
```

## Step 1.8: Wait for Activation
```
⏳ Wait 5-10 minutes
📧 You'll get email: "Your AWS Account is Ready"
```

---

# PART 2: SIGN IN TO AWS
*Time: 1 minute*

## Step 2.1: Go to Console
```
1. Open: console.aws.amazon.com
2. Select "Root user"
3. Enter your email
4. Click "Next"
5. Enter password
6. Click "Sign in"
```

## Step 2.2: Select Region
```
1. Look at TOP RIGHT corner
2. Click region name (might say "Ohio" or "N. Virginia")
3. Select: "US East (N. Virginia) us-east-1"
```

---

# PART 3: CREATE SSH KEY
*Time: 2 minutes*

This is a special file that lets you connect to your server.

## Step 3.1: Go to EC2
```
1. Click search bar at top
2. Type: EC2
3. Click "EC2" in results
```

## Step 3.2: Create Key Pair
```
1. Left sidebar → scroll to "Network & Security"
2. Click "Key Pairs"
3. Click orange "Create key pair" button
4. Name: edugen-key
5. Key pair type: RSA ✅
6. Format: .pem ✅
7. Click "Create key pair"
8. File "edugen-key.pem" downloads automatically

⚠️ SAVE THIS FILE! You cannot download it again!
```

---

# PART 4: LAUNCH SERVER (EC2)
*Time: 5 minutes*

## Step 4.1: Start Instance Launch
```
1. Left sidebar → Click "Instances"
2. Click orange "Launch instances" button
```

## Step 4.2: Name Server
```
In "Name and tags":
→ Type: edugen-server
```

## Step 4.3: Choose Ubuntu
```
In "Application and OS Images":
1. Click "Ubuntu" (orange logo)
2. Keep "Ubuntu Server 22.04 LTS"
3. Verify: Shows "Free tier eligible"
```

## Step 4.4: Choose Size
```
In "Instance type":
1. Click dropdown
2. Select: t2.micro
3. Shows: "1 vCPU, 1 GiB Memory - Free tier eligible"
```

## Step 4.5: Select Key
```
In "Key pair (login)":
1. Click dropdown
2. Select: edugen-key
```

## Step 4.6: Network Settings
```
1. Click "Edit" button (right side)

2. Auto-assign public IP: Change to "Enable"

3. Firewall (security groups):
   → Select "Create security group"
   → Security group name: edugen-sg
   → Description: Video Generator
```

## Step 4.7: Add Firewall Rules
```
You see SSH rule. Add 3 more:

RULE 1:
1. Click "Add security group rule"
2. Type: Custom TCP
3. Port range: 8000
4. Source: Anywhere
5. Description: API

RULE 2:
1. Click "Add security group rule"  
2. Type: HTTP
3. Source: Anywhere

RULE 3:
1. Click "Add security group rule"
2. Type: HTTPS  
3. Source: Anywhere
```

## Step 4.8: Storage
```
In "Configure storage":
1. Change 8 → 30
2. Keep gp3
```

## Step 4.9: Launch
```
1. Click orange "Launch instance" button
2. Wait for "Success" message
3. Click "View all instances"
```

## Step 4.10: Get IP Address
```
1. Wait until "Instance state" = Running (green)
2. Wait until "Status check" = 2/2 checks passed
3. Click checkbox next to "edugen-server"
4. Look at details below
5. Find "Public IPv4 address"
6. COPY THIS IP (click copy icon)

Example: 54.123.45.67
```

---

# PART 5: CONNECT FROM WINDOWS
*Time: 5 minutes*

## Step 5.1: Open PowerShell
```
1. Press: Windows key + X
2. Click: "Terminal" or "Windows PowerShell"
```

## Step 5.2: Create SSH Folder
```powershell
mkdir -Force $HOME\.ssh
```

## Step 5.3: Move Key File
```powershell
Move-Item "$HOME\Downloads\edugen-key.pem" "$HOME\.ssh\edugen-key.pem" -Force
```

## Step 5.4: Connect to Server
Replace YOUR_IP with your IP from Step 4.10:
```powershell
ssh -i "$HOME\.ssh\edugen-key.pem" ubuntu@YOUR_IP
```

Example:
```powershell
ssh -i "$HOME\.ssh\edugen-key.pem" ubuntu@54.123.45.67
```

## Step 5.5: Accept Connection
```
When asked "Are you sure...?"
1. Type: yes
2. Press: Enter
```

## Step 5.6: Verify
```
You should see:
ubuntu@ip-xxx-xxx-xxx-xxx:~$

✅ You're connected to AWS!
```

---

# PART 6: UPLOAD YOUR CODE
*Time: 5 minutes*

**Open NEW PowerShell window** (keep SSH window open)

## Step 6.1: Create ZIP
In NEW PowerShell:
```powershell
Compress-Archive -Path "C:\Users\Mahak\devForge\*" -DestinationPath "$HOME\devForge.zip" -Force
```

## Step 6.2: Upload ZIP
Replace YOUR_IP:
```powershell
scp -i "$HOME\.ssh\edugen-key.pem" "$HOME\devForge.zip" ubuntu@YOUR_IP:~/
```

Wait for upload (~2-5 minutes depending on internet)

---

# PART 7: SETUP SERVER
*Time: 15-20 minutes*

**Go back to SSH window** (where you're connected to ubuntu@...)

## Step 7.1: Update System
```bash
sudo apt update && sudo apt upgrade -y
```
If asked questions, press Y and Enter.
Wait 1-2 minutes.

## Step 7.2: Install Tools
```bash
sudo apt install -y unzip python3-pip python3-venv ffmpeg git curl
```

## Step 7.3: Extract Code
```bash
unzip ~/devForge.zip -d ~/devForge
cd ~/devForge
```

## Step 7.4: Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 7.5: Download AI Model
```bash
ollama serve &
sleep 10
ollama pull phi3:mini
```
⏳ This downloads ~2.3GB. Wait 5-10 minutes.

## Step 7.6: Setup Python
```bash
cd ~/devForge
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 7.7: Test API
```bash
python -m uvicorn web_app.api:app --host 0.0.0.0 --port 8000
```

## Step 7.8: Verify in Browser
Open your browser and go to:
```
http://YOUR_IP:8000/api/health
```

You should see:
```json
{"status":"healthy","ollama_available":true}
```

Press Ctrl+C in SSH to stop test.

---

# PART 8: RUN FOREVER
*Time: 2 minutes*

## Step 8.1: Create Service File
```bash
sudo tee /etc/systemd/system/edugen.service << 'EOF'
[Unit]
Description=Educational Video Generator
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/devForge
Environment=PATH=/home/ubuntu/devForge/venv/bin
ExecStart=/home/ubuntu/devForge/venv/bin/python -m uvicorn web_app.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

## Step 8.2: Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable edugen
sudo systemctl start edugen
```

## Step 8.3: Check Status
```bash
sudo systemctl status edugen
```
Should show: **active (running)** in green

---

# PART 9: DEPLOY FRONTEND
*Time: 10 minutes*

## Step 9.1: Push to GitHub
In Windows PowerShell:
```powershell
cd C:\Users\Mahak\devForge
git add .
git commit -m "Ready for deploy"
git push origin main
```

## Step 9.2: Sign Up for Vercel
```
1. Go to: vercel.com
2. Click "Sign Up"
3. Click "Continue with GitHub"
4. Authorize Vercel
```

## Step 9.3: Import Project
```
1. Click "Add New..." → "Project"
2. Find "devForge" repository
3. Click "Import"
```

## Step 9.4: Configure
```
1. Framework Preset: Vite
2. Root Directory: Click "Edit" → type "frontend"
3. Build Command: npm run build
4. Output Directory: dist
```

## Step 9.5: Add API URL
```
1. Click "Environment Variables"
2. Name: VITE_API_URL
3. Value: http://YOUR_EC2_IP:8000
4. Click "Add"
```

## Step 9.6: Deploy
```
1. Click "Deploy"
2. Wait 2-3 minutes
3. Get your URL: something.vercel.app
```

---

# PART 10: FINAL SETUP

## Step 10.1: Update CORS
In SSH window:
```bash
echo "CORS_ORIGINS=https://your-app.vercel.app" | sudo tee /home/ubuntu/devForge/.env
sudo systemctl restart edugen
```

Replace "your-app.vercel.app" with your actual Vercel URL.

---

# ✅ DONE!

## Your URLs
| What | URL |
|------|-----|
| Frontend | https://your-app.vercel.app |
| Backend | http://YOUR_IP:8000 |
| API Health | http://YOUR_IP:8000/api/health |

---

# 📋 COMMON COMMANDS

## Connect to Server
```powershell
ssh -i "$HOME\.ssh\edugen-key.pem" ubuntu@YOUR_IP
```

## View Logs
```bash
sudo journalctl -u edugen -f
```

## Restart API
```bash
sudo systemctl restart edugen
```

## Check Status
```bash
sudo systemctl status edugen
```

---

# 🆘 TROUBLESHOOTING

## Can't Connect via SSH?
1. Check IP is correct
2. Check security group has port 22 open
3. Check key file exists: `Test-Path "$HOME\.ssh\edugen-key.pem"`

## API Not Responding?
```bash
sudo systemctl status edugen
sudo journalctl -u edugen --no-pager -n 50
```

## Ollama Not Working?
```bash
sudo systemctl restart ollama
ollama list
```

## Out of Memory?
Upgrade to t3.medium or add swap:
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

# 💰 COST ESTIMATE

| Resource | Free Tier | After Free Tier |
|----------|-----------|-----------------|
| t2.micro | 750 hrs/month FREE | ~$8/month |
| 30GB storage | FREE | ~$2.40/month |
| Data transfer | 100GB FREE | $0.09/GB |

**First year**: Mostly FREE  
**After**: ~$15-20/month (t2.micro)
