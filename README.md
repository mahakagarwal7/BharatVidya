# 🎬 BharatVidya - AI-Powered Educational Video Generator

> Transform any concept into beautifully animated educational videos in 10+ languages

[![Vercel Deployment](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel)](https://dev-forge-one.vercel.app/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react)](https://react.dev/)
[![AWS EC2](https://img.shields.io/badge/Deployment-AWS%20EC2-FF9900?logo=amazon-ec2)](https://aws.amazon.com/ec2/)

---

## 📖 Overview

**BharatVidya** is a cutting-edge AI-powered platform that generates engaging, animated educational videos from simple text descriptions. The system automatically:

1. **Plans** - Extracts structured content using Ollama LLM
2. **Narrates** - Generates natural speech in 10+ languages using Edge-TTS
3. **Animates** - Creates smooth animations with OpenCV/MoviePy
4. **Delivers** - Streams final MP4 videos via AWS S3

Perfect for educators, content creators, and e-learning platforms looking for automated video generation at scale.

**Live Demo:** https://dev-forge-one.vercel.app/

---

## ✨ Key Features

### 🎯 Intelligent Content Generation
- **Multi-language Support**: English, Hindi, Punjabi, Telugu, Bengali, Tamil, Spanish, French, German, Chinese, Japanese, Korean
- **Smart Planning**: Ollama-powered content extraction with structured educational narratives
- **Topic-based Animations**: Enhanced visuals for specific educational concepts with optional animations toggle

### 🗣️ High-Quality Narration
- **Edge-TTS Integration**: Professional text-to-speech in 10+ languages
- **Audio Processing**: pydub-based audio enhancement and mixing
- **Voice Customization**: Support for different voice profiles per language

### 🎨 Advanced Video Rendering
- **MoviePy Framework**: Professional-grade video composition
- **Smooth Animations**: Floating elements, gradient effects, and smooth transitions
- **Customizable Visuals**: Toggle animations on/off per generation

### 💾 Cloud Storage & Management
- **AWS S3 Integration**: Secure video storage and streaming
- **Job Management**: Redis-backed job queue for async video processing
- **Video Gallery**: Browse and manage all generated videos

### 🌈 Modern User Interface
- **React 19 Frontend**: Ultra-responsive, interactive UI
- **Dark/Light Theme**: Professional theming system with CSS custom properties
- **Real-time Progress**: WebSocket-ready status polling for live generation updates
- **Glassmorphism Design**: Modern glassmorphic UI with smooth animations
- **Mobile Responsive**: Fully optimized for all device sizes

### ⚡ High Performance
- **Async Processing**: FastAPI background tasks for non-blocking operations
- **Batch Processing**: Handle multiple concurrent video generations
- **Optimized Rendering**: Efficient MoviePy pipeline with caching
- **Smart Caching**: Reuse of common animations and assets

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   React 19 Web Application          │
│   (Deployed on Vercel)              │
│   https://dev-forge-one.vercel.app/ │
│                                     │
│ • Input topic/concept               │
│ • Select language                   │
│ • Toggle animations                 │
│ • View video gallery                │
│ • Dark/Light theme                  │
└────────────────┬────────────────────┘
                 │ HTTPS
                 │ /api/generate
                 │ /api/status
                 │ /api/videos
                 │
        ┌────────▼─────────────────────────┐
        │  FastAPI Backend (BharatVidya)   │
        │  AWS EC2 Instance                │
        │                                  │
        │ ┌────────────────────────────┐   │
        │ │ API Endpoints              │   │
        │ ├────────────────────────────┤   │
        │ │ POST /api/generate         │   │
        │ │ GET  /api/status/{id}      │   │
        │ │ GET  /api/videos           │   │
        │ │ GET  /api/video/{id}       │   │
        │ │ GET  /api/topics           │   │
        │ │ GET  /api/health           │   │
        │ └────────────────────────────┘   │
        │                                  │
        │ ┌────────────────────────────┐   │
        │ │ Processing Pipeline        │   │
        │ ├────────────────────────────┤   │
        │ │ 1. Content Planner         │   │
        │ │    (Ollama LLM)            │   │
        │ │ 2. Narrator                │   │
        │ │    (Edge-TTS)              │   │
        │ │ 3. Animator                │   │
        │ │    (MoviePy/OpenCV)        │   │
        │ │ 4. Renderer                │   │
        │ │    (Video Output)          │   │
        │ └────────────────────────────┘   │
        └────────┬─────────────────────────┘
                 │
        ┌────────┴──────────┬──────────────┐
        │                   │              │
   ┌────▼──────┐      ┌────▼──────┐  ┌───▼─────┐
   │  Ollama   │      │ Edge-TTS  │  │MoviePy  │
   │   (LLM)   │      │  (Voice)  │  │(Render) │
   └───────────┘      └───────────┘  └─────────┘
        │
   ┌────▼────────────────────────────┐
   │ AWS S3 Bucket                   │
   │ (Video Storage & Streaming)     │
   └─────────────────────────────────┘
```

---

## 📁 Project Structure

```
BharatVidya/
│
├── frontend/                      # React 19 Web Application
│   ├── src/
│   │   ├── App.jsx               # Main React component
│   │   ├── App.css               # Component styles
│   │   ├── index.css             # Global styles & theme system
│   │   ├── main.jsx              # Entry point
│   │   └── assets/               # Static assets
│   ├── public/                    # Public files
│   ├── package.json              # React dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── eslint.config.js          # ESLint rules
│   ├── index.html                # HTML entry point
│   └── vercel.json               # Vercel deployment config
│
├── web_app/                       # FastAPI Backend
│   ├── __init__.py
│   ├── api.py                    # FastAPI app & routes
│   ├── models.py                 # Pydantic data models
│   ├── jobs.py                   # Job queue management
│   ├── video_service.py          # Video generation service
│   └── s3_service.py             # AWS S3 integration
│
├── src/                           # Core Processing Engine
│   ├── main.py                   # CLI entrypoint
│   ├── animator.py               # Orchestrator (planner + narrator + renderer)
│   ├── planner.py                # ContentPlanner (Ollama integration)
│   ├── narrator.py               # Narrator (Edge-TTS integration)
│   ├── renderer.py               # MoviePyRenderer (video composition)
│   ├── card_generator.py         # Visual card generation
│   ├── animation_clips.py        # Animation helper functions
│   ├── latex_renderer.py         # LaTeX to image rendering
│   ├── local_llm_client.py       # Ollama LLM client
│   ├── topic_router.py           # Topic-specific animation routing
│   ├── utils.py                  # Utility functions
│   ├── __pycache__/              # Compiled Python cache
│   ├── domain_engines/           # Specialized animation engines
│   └── outputs/                  # Generated artifacts
│
├── deploy/                        # Deployment Configuration
│   ├── Dockerfile                # Docker container specification
│   ├── docker-compose.yml        # Docker Compose orchestration
│   ├── setup_ec2.sh              # EC2 automated setup script
│   ├── deploy_backend.sh         # Backend deployment script
│   ├── DEPLOYMENT.md             # Detailed deployment guide
│   ├── AWS_GETTING_STARTED.md    # AWS setup instructions
│   ├── WINDOWS_DEPLOYMENT_GUIDE.md # Windows-specific setup
│   └── aws/
│       └── cloudformation.yaml   # AWS CloudFormation template
│
├── outputs/                       # Runtime Outputs
│   ├── plans/                    # Generated JSON content plans
│   ├── audio/                    # Generated audio files
│   ├── generated_images/         # Rendered visual assets
│   └── videos/                   # Cached video files
│
├── test_frames/                  # Test video frames
│
├── training/                      # Training & Fine-tuning
│   ├── database_prep.py
│   ├── plan_to_example.py        # Data pipeline
│   ├── plan_validator.py
│   ├── train_slm.py              # SLM fine-tuning
│   ├── training_pipeline.py      # Training orchestrator
│   ├── sample_data.jsonl         # Sample training data
│ 
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── run.py                        # Application launcher
├── plan_validator.py             # Plan validation utilities
├── test_topics.py                # Topic testing suite
├── test.py                       # General test suite
└── README.md                     # This file
```

---

## 🛠️ Tech Stack

### Frontend
- **React 19.2.0** - Modern component framework
- **Vite 8.0.0-beta.13** - Lightning-fast build tool
- **Tailwind CSS 4.2.1** - Utility-first CSS framework
- **CSS Custom Properties** - Advanced theming system

### Backend
- **FastAPI 0.109.0+** - High-performance Python web framework
- **Uvicorn 0.27.0+** - ASGI server
- **Pydantic 2.5.0+** - Data validation
- **Ollama** - Local LLM for content generation(Phi3:mini)
- **Edge-TTS 6.1.0+** - Text-to-speech synthesis
- **MoviePy 1.0.3** - Video composition & rendering
- **OpenCV 4.12.0** - Image processing
- **Pillow 12.0.0** - Image manipulation
- **Boto3 1.34.0+** - AWS S3 integration

### Deployment & Infrastructure
- **Docker & Docker Compose** - Containerization
- **AWS EC2** - Backend hosting
- **AWS S3** - Video storage
- **Vercel** - Frontend hosting
- **AWS CloudFormation** - Infrastructure as Code

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** - Backend runtime
- **Node.js 18+** - Frontend development
- **Ollama** - Local LLM (for content generation)
- **FFmpeg** - Video processing (MoviePy dependency)
- **AWS Account** (optional, for cloud deployment)
- **Git** - Version control

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/BharatVidya.git
cd BharatVidya
```

#### 2. Backend Setup

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Start Ollama (in separate terminal)
ollama serve
ollama pull phi3:mini  # Download a model

# Run backend
python run.py
# OR use FastAPI directly
uvicorn web_app.api:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend will be available at http://localhost:5173

# Build for production
npm run build
```

#### 4. Generate Your First Video (CLI)

```bash
# Using CLI with Python
python -m src.main "Explain photosynthesis" --lang en --animations

# Options:
#   --lang [code]      : Language code (en, hi, pa, te, bn, ta, es, fr, de, zh, ja, ko)
#   --animations       : Include topic-specific animations
#   --no-animations    : Disable animations

# Example outputs
# ✅ Video created: outputs/videos/video_abc123.mp4
# ✅ Plan saved: outputs/plans/plan_def456.json
```

---

## 📡 API Endpoints

### Base URL: `https://api.bharatvidya.com/api` (Production)
### Local: `http://localhost:8000/api`

#### 1. **Generate Video**
```bash
POST /api/generate
Content-Type: application/json

{
  "concept": "Newton's Laws of Motion",
  "language": "en",
  "enable_animations": true
}

Response: 200 OK
{
  "job_id": "uuid-1234-5678",
  "status": "processing",
  "message": "Video generation started"
}
```

#### 2. **Check Job Status**
```bash
GET /api/status/{job_id}

Response: 200 OK
{
  "job_id": "uuid-1234-5678",
  "status": "processing|complete|failed",
  "progress": 45,
  "step": "Rendering video frames...",
  "video_url": "https://s3.amazonaws.com/videos/...",
  "error": null
}
```

#### 3. **List All Videos**
```bash
GET /api/videos

Response: 200 OK
{
  "videos": [
    {
      "job_id": "uuid-1234",
      "concept": "Photosynthesis",
      "language": "en",
      "video_url": "https://s3.amazonaws.com/...",
      "created_at": "2026-03-03T10:30:00Z",
      "status": "complete"
    }
  ],
  "total": 15
}
```

#### 4. **Get Supported Topics**
```bash
GET /api/topics

Response: 200 OK
{
  "supported_languages": [
    "en", "hi", "pa", "te", "bn", "ta", "es", "fr", "de", "zh", "ja", "ko"
  ],
  "example_topics": [
    "Photosynthesis",
    "DNA Structure",
    "Newton's Laws",
    "Quantum Computing"
  ]
}
```

#### 5. **Health Check**
```bash
GET /api/health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2026-03-03T10:30:00Z",
  "version": "1.0.0"
}
```

---

## 🎬 Video Generation Pipeline

```
User Input (Concept)
        ↓
┌───────────────────────┐
│  Content Planner      │  → Ollama LLM extracts structured content
├───────────────────────┤     • Breaks down topic into sections
│  JSON Output          │     • Identifies key facts
│  {title, summary,     │     • Generates speaking points
│   sections, facts}    │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Narrator             │  → Edge-TTS generates audio narration
├───────────────────────┤     • Text-to-speech in selected language
│  Audio File           │     • Natural-sounding speech
│  (.wav)               │     • Auto-adjusts for optimal playback
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Animator             │  → Topic-specific animations
├───────────────────────┤     • Generates visual assets
│  Animation Frames &   │     • Creates smooth transitions
│  Visual Elements      │     • Optional animated cards
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Renderer             │  → MoviePy composition engine
├───────────────────────┤     • Combines audio + visuals
│  MP4 Video            │     • Optimized codec settings
│  (H.264, AAC)         │     • HD quality (1280x720)
└───────────────────────┘
        ↓
┌───────────────────────┐
│  S3 Storage           │  → AWS S3 upload
├───────────────────────┤     • Video streaming ready
│  Shareable URL        │     • CDN distribution
│  (Permanent)          │     • Playback ready
└───────────────────────┘
```

---

## 🌐 Supported Languages

| Code | Language | Supported |
|------|----------|-----------|
| `en` | English | ✅ |
| `hi` | Hindi | ✅ |
| `pa` | Punjabi | ✅ |
| `te` | Telugu | ✅ |
| `bn` | Bengali | ✅ |
| `ta` | Tamil | ✅ |
| `es` | Spanish | ✅ |
| `fr` | French | ✅ |
| `de` | German | ✅ |
| `zh` | Chinese | ✅ |
| `ja` | Japanese | ✅ |
| `ko` | Korean | ✅ |

---

## 🚢 Production Deployment

### Quick Deploy (Automated)

#### Frontend (Vercel)
```bash
# Link your Vercel project
vercel link

# Deploy
vercel --prod
```

#### Backend (AWS EC2 - BharatVidya Instance)
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Run automated setup
bash deploy/setup_ec2.sh

# Or use Docker
docker-compose -f deploy/docker-compose.yml up -d
```

### Detailed Deployment Guide

See [DEPLOYMENT.md](deploy/DEPLOYMENT.md) for:
- Manual AWS EC2 setup
- Docker containerization
- CloudFormation template
- Environment configuration
- SSL/TLS setup
- S3 bucket configuration
- GitHub Actions CI/CD

See [AWS_GETTING_STARTED.md](deploy/AWS_GETTING_STARTED.md) for AWS-specific setup.

See [WINDOWS_DEPLOYMENT_GUIDE.md](deploy/WINDOWS_DEPLOYMENT_GUIDE.md) for Windows development setup.

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434        # Local Ollama instance
OLLAMA_MODEL=phi3:mini                         # LLM model to use

# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=bharatvidya-videos

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production                        # development|production

# CORS Configuration
CORS_ORIGINS=https://dev-forge-one.vercel.app,https://*.vercel.app

# Feature Flags
ENABLE_NARRATION=true                        # Enable/disable TTS
ENABLE_ANIMATIONS=true                       # Enable/disable animations
```

---

## 📊 Features Breakdown

### Core Capabilities
- ✅ Automatic content planning from text
- ✅ Multi-language support (10+ languages)
- ✅ Professional narration with Edge-TTS
- ✅ Smooth animations and transitions
- ✅ HD video rendering (1280x720)
- ✅ Cloud storage via AWS S3
- ✅ Real-time progress tracking
- ✅ Video gallery and management

### UI/UX Features
- ✅ Modern glassmorphism design
- ✅ Dark/Light theme toggle
- ✅ Responsive mobile design
- ✅ Real-time status updates
- ✅ Video player with controls
- ✅ Download functionality
- ✅ Video metadata display
- ✅ Example topic suggestions

### Backend Features
- ✅ Async job processing
- ✅ API rate limiting
- ✅ CORS support
- ✅ Error handling & recovery
- ✅ AWS S3 integration
- ✅ Database support
- ✅ Health checks
- ✅ Comprehensive logging

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Test specific module
python -m pytest tests/test_animator.py -v

# Run with coverage
python -m pytest --cov=src

# Test video generation
python test.py

# Test topics
python test_topics.py

# Validate plans
python plan_validator.py
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Video Generation Time | 2-5 minutes |
| Supported Concurrent Jobs | 5+ (configurable) |
| Maximum Video Duration | 30 minutes |
| Output Video Quality | 1280x720 HD |
| Audio Quality | 44.1kHz, 128kbps AAC |
| Frontend Load Time | <2 seconds |
| API Response Time | <500ms (avg) |

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Ollama Connection Failed
```bash
# Ensure Ollama is running
ollama serve

# Check if accessible
curl http://localhost:11434/api/tags
```

#### 2. AWS S3 Upload Issues
```bash
# Verify AWS credentials in .env
# Check S3 bucket permissions
aws s3 ls s3://your-bucket-name

# Check IAM policy for S3 access
```

#### 4. Video Generation Hangs
```bash
# Check MoviePy/FFmpeg installation
ffmpeg -version

# Increase timeout values in video_service.py
# Check system resources (RAM, CPU)
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with clear commit messages
4. **Write** tests for new functionality
5. **Submit** a pull request

### Code Style
- Follow PEP 8 for Python code
- Use ESLint rules for JavaScript/React
- Write clear docstrings and comments
- Keep components reusable

### Reporting Issues
Please use GitHub Issues for bug reports and feature requests.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM platform
- **MoviePy** - Video composition library
- **FastAPI** - Modern Python web framework
- **React** - UI framework
- **Vercel** - Frontend hosting
- **AWS** - Cloud infrastructure

---

*Transform education with AI-powered video generation*
