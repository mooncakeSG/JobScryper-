# Auto Applyer - Complete Setup Guide

## 🎯 Overview

Auto Applyer is a comprehensive job search and application automation platform that combines AI-powered resume analysis, multi-source job scraping, and intelligent application tracking. This guide will help you set up the project for development, testing, and production use.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Configuration](#configuration)
5. [Development Setup](#development-setup)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## 🔧 Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **Git**: Latest version
- **Docker**: 20.10+ (for containerized deployment)
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: 2GB free space

### Required Software

#### Python Dependencies
```bash
# Core Python packages (automatically installed)
- Python 3.11+
- pip (Python package manager)
- virtualenv or venv (for environment isolation)
```

#### Node.js Dependencies
```bash
# Frontend dependencies (automatically installed)
- Node.js 18.0+
- npm (Node package manager)
```

#### System Dependencies (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv
sudo apt-get install -y build-essential libssl-dev libffi-dev
sudo apt-get install -y curl wget git

# macOS (using Homebrew)
brew install python3 node git
brew install openssl readline sqlite3

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel python3-pip
sudo yum install openssl-devel libffi-devel
```

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/auto-applyer.git
cd auto-applyer

# 2. Start with Docker Compose
docker-compose up --build

# 3. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/auto-applyer.git
cd auto-applyer

# 2. Run the automated setup script
python setup.py

# 3. Start the application
python start_app.py
```

## 📦 Detailed Installation

### Step 1: Repository Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/auto-applyer.git
cd auto-applyer

# Verify the structure
ls -la
# Should show: backend/, job-frontend/, requirements.txt, etc.
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install Playwright browsers (for web automation)
playwright install

# Initialize database
python -c "from database.init_db import init_database; init_database()"

# Test backend installation
python -c "from main import app; print('Backend setup successful!')"
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd ../job-frontend

# Install Node.js dependencies
npm install

# Verify installation
npm run build

# Test frontend
npm run dev
# Should start on http://localhost:3000
```

### Step 4: Environment Configuration

```bash
# Create environment files
cd ..

# Backend environment
cat > backend/.env << EOF
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/auto_applyer.db
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
JOBSPY_API_KEY=your-jobspy-api-key
EOF

# Frontend environment
cat > job-frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Auto Applyer
NEXT_PUBLIC_ENVIRONMENT=development
EOF
```

## ⚙️ Configuration

### API Keys Setup

The application requires several API keys for full functionality:

#### 1. Groq API (Required for AI features)
```bash
# Get your API key from: https://console.groq.com/
GROQ_API_KEY=your-groq-api-key-here
```

#### 2. OpenAI API (Optional, for advanced AI features)
```bash
# Get your API key from: https://platform.openai.com/
OPENAI_API_KEY=your-openai-api-key-here
```

#### 3. JobSpy API (Required for job scraping)
```bash
# Get your API key from: https://jobspy.com/
JOBSPY_API_KEY=your-jobspy-api-key-here
```

### Database Configuration

#### SQLite (Default - Development)
```bash
DATABASE_URL=sqlite:///./data/auto_applyer.db
```

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/auto_applyer
```

### Environment Variables Reference

#### Backend (.env)
```bash
# Application
ENVIRONMENT=development|production
SECRET_KEY=your-secret-key
DEBUG=true|false

# Database
DATABASE_URL=sqlite:///./data/auto_applyer.db

# API Keys
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
JOBSPY_API_KEY=your-jobspy-api-key

# Security
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

#### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Auto Applyer

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
NEXT_PUBLIC_DEBUG=true

# Features
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
```

## 🛠️ Development Setup

### Project Structure

```
Auto Applyer/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── database/          # Database models and migrations
├── job-frontend/          # Next.js frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── tests/                 # Test suite
├── docs/                  # Documentation
├── docker-compose.yml     # Container orchestration
└── requirements.txt       # Main Python dependencies
```

### Development Workflow

#### 1. Backend Development
```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run in development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest ../tests/ -v

# Run specific test file
pytest ../tests/unit/test_applications.py -v
```

#### 2. Frontend Development
```bash
cd job-frontend

# Start development server
npm run dev

# Run linting
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

#### 3. Full Stack Development
```bash
# Start both services
python start_app.py

# Or use the launcher
streamlit run launcher.py
```

### Code Quality Tools

#### Backend
```bash
# Install development dependencies
pip install black flake8 mypy isort

# Format code
black backend/
isort backend/

# Lint code
flake8 backend/
mypy backend/
```

#### Frontend
```bash
# Install development dependencies
npm install --save-dev prettier eslint-config-prettier

# Format code
npm run format

# Lint code
npm run lint
```

## 🧪 Testing

### Running Tests

#### Backend Tests
```bash
cd backend

# Run all tests
pytest ../tests/ -v

# Run with coverage
pytest ../tests/ --cov=backend --cov-report=html

# Run specific test categories
pytest ../tests/unit/ -v
pytest ../tests/integration/ -v
pytest ../tests/performance/ -v

# Run tests in parallel
pytest ../tests/ -n auto
```

#### Frontend Tests
```bash
cd job-frontend

# Run tests (when implemented)
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

#### End-to-End Tests
```bash
# Install Playwright
playwright install

# Run E2E tests
playwright test

# Run specific test file
playwright test tests/e2e/job-search.spec.ts
```

### Test Data Setup

```bash
# Create test database
python -c "from database.init_db import init_test_database; init_test_database()"

# Load sample data
python scripts/load_sample_data.py
```

## 🚀 Deployment

### Production Deployment with Docker

#### 1. Build Production Images
```bash
# Build all services
docker-compose -f docker-compose.production.yml build

# Or build individually
docker build -t auto-applyer-backend ./backend
docker build -t auto-applyer-frontend ./job-frontend
```

#### 2. Environment Setup
```bash
# Create production environment file
cat > .env.production << EOF
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/auto_applyer
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
JOBSPY_API_KEY=your-jobspy-api-key
EOF
```

#### 3. Deploy
```bash
# Start production services
docker-compose -f docker-compose.production.yml up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Cloud Deployment

#### AWS Deployment
```bash
# Using AWS ECS
aws ecs create-cluster --cluster-name auto-applyer
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster auto-applyer --service-name auto-applyer-service --task-definition auto-applyer:1
```

#### Google Cloud Deployment
```bash
# Using Google Cloud Run
gcloud run deploy auto-applyer-backend --source ./backend
gcloud run deploy auto-applyer-frontend --source ./job-frontend
```

#### Heroku Deployment
```bash
# Deploy to Heroku
heroku create auto-applyer-app
heroku config:set ENVIRONMENT=production
heroku config:set GROQ_API_KEY=your-key
git push heroku main
```

### SSL and Domain Setup

#### Using Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Environment Issues
```bash
# Problem: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Problem: Permission denied
# Solution: Use sudo (Linux/macOS) or run as administrator (Windows)
sudo pip install -r requirements.txt
```

#### 2. Node.js Issues
```bash
# Problem: npm install fails
# Solution: Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Problem: Port already in use
# Solution: Kill process or change port
lsof -ti:3000 | xargs kill -9
# or
npm run dev -- --port 3001
```

#### 3. Database Issues
```bash
# Problem: Database connection failed
# Solution: Check database URL and permissions
python -c "from database.connection import test_connection; test_connection()"

# Problem: Migration errors
# Solution: Reset database and re-run migrations
rm -f data/auto_applyer.db
python -c "from database.init_db import init_database; init_database()"
```

#### 4. API Key Issues
```bash
# Problem: API calls failing
# Solution: Verify API keys are set correctly
python -c "import os; print('GROQ_API_KEY:', bool(os.getenv('GROQ_API_KEY')))"
```

#### 5. Docker Issues
```bash
# Problem: Container won't start
# Solution: Check logs and rebuild
docker-compose logs backend
docker-compose down
docker-compose build --no-cache
docker-compose up

# Problem: Port conflicts
# Solution: Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Performance Issues

#### 1. Slow Startup
```bash
# Enable caching
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Use production mode
export ENVIRONMENT=production
```

#### 2. Memory Issues
```bash
# Monitor memory usage
python -c "import psutil; print(psutil.virtual_memory())"

# Optimize database queries
python scripts/optimize_database.py
```

### Debug Mode

#### Backend Debug
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with debugger
python -m pdb main.py
```

#### Frontend Debug
```bash
# Enable React DevTools
npm install --save-dev react-devtools

# Run in development mode
npm run dev
```

## 🤝 Contributing

### Development Setup for Contributors

#### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/auto-applyer.git
cd auto-applyer

# Add upstream remote
git remote add upstream https://github.com/original/auto-applyer.git
```

#### 2. Create Feature Branch
```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Test thoroughly
# Commit with descriptive message
git commit -m "feat: add new feature description"
```

#### 3. Submit Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Include:
# - Description of changes
# - Screenshots (if UI changes)
# - Test results
# - Related issues
```

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions
- Maximum line length: 88 characters (Black)
- Use meaningful variable names

#### TypeScript/JavaScript (Frontend)
- Follow ESLint configuration
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Write meaningful component names

### Testing Requirements

#### Before Submitting PR
```bash
# Run all tests
pytest tests/ -v
npm test

# Check code quality
black backend/
flake8 backend/
npm run lint

# Ensure no new warnings
pytest tests/ --disable-warnings
```

## 📚 Additional Resources

### Documentation
- [API Documentation](http://localhost:8000/docs) (when running)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

### External Dependencies
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Groq API Documentation](https://console.groq.com/docs)

### Support
- [GitHub Issues](https://github.com/mooncakesg/auto-applyer/issues)
- [Discussions](https://github.com/mooncakesg/auto-applyer/discussions)
- [Wiki](https://github.com/mooncakesg/auto-applyer/wiki)

## 🎉 Getting Started Checklist

- [ ] Clone the repository
- [ ] Install Python 3.11+
- [ ] Install Node.js 18+
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Set up API keys
- [ ] Initialize database
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Access application at http://localhost:3000
- [ ] Run tests to verify installation
- [ ] Explore the documentation

## 📞 Need Help?

If you encounter any issues during setup:

1. **Check the troubleshooting section** above
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information:
   - Operating system and version
   - Python and Node.js versions
   - Error messages and logs
   - Steps to reproduce the issue

---

**Happy coding! 🚀**

*This setup guide is maintained by the Auto Applyer development. For the latest updates, check the [GitHub repository](https://github.com/mooncakesg/auto-applyer).* 