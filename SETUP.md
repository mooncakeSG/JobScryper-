# Auto Applyer - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git installed
- Groq API key (free at https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/mooncakeSG/JobScryper-.git
cd JobScryper-
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
# Copy the example
cp .env.example .env
```

Edit `.env` file with your API keys:
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key

# Optional: Other API keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔧 Detailed Setup Instructions

### System Requirements

#### Minimum Requirements:
- **OS**: Windows 10, macOS 10.15, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection

#### Recommended Requirements:
- **Python**: 3.10 or higher
- **RAM**: 16GB for optimal performance
- **Storage**: 10GB free space (for logs and cached data)

### Python Environment Setup

#### Option 1: Using Anaconda (Recommended)
```bash
# Install Anaconda from https://www.anaconda.com/products/distribution
conda create -n auto_applyer python=3.10
conda activate auto_applyer
pip install -r requirements.txt
```

#### Option 2: Using pipenv
```bash
pip install pipenv
pipenv install
pipenv shell
```

#### Option 3: Using Poetry
```bash
pip install poetry
poetry install
poetry shell
```

### API Keys Setup

#### 1. Groq API Key (Required)
1. Visit https://console.groq.com
2. Create a free account
3. Generate an API key
4. Add to your `.env` file:
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

#### 2. Optional API Keys
- **OpenAI**: For additional AI features (https://platform.openai.com)
- **Anthropic**: For Claude integration (https://console.anthropic.com)

### Configuration Files

#### Create Required Directories
```bash
mkdir -p assets reports logs
```

#### Environment Configuration
```env
# .env file configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama3-8b-8192
GROQ_MAX_TOKENS=3000
GROQ_TEMPERATURE=0.7

# Database (optional)
DATABASE_URL=sqlite:///auto_applyer.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# UI Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

## 🎯 Feature-Specific Setup

### Resume Upload
1. Create `assets/` directory
2. Supported formats: PDF, DOCX, TXT
3. Maximum file size: 10MB

### Job Search Configuration
- **South African Users**: Pre-configured for SA job sites
- **International Users**: Adjust location settings in the app
- **Supported Job Sites**: Indeed, LinkedIn, Google Jobs

### AI Resume Suggestions
- Requires Groq API key
- Free tier: 10,000 requests/month
- Average response time: 3-5 seconds

## 🔍 Troubleshooting

### Common Issues

#### 1. "Module not found" Error
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Groq API Key Not Working
- Verify API key is correct (starts with `gsk_`)
- Check account quota at https://console.groq.com
- Ensure no extra spaces in `.env` file

#### 3. Job Search Returns No Results
- Check internet connection
- Verify location spelling
- Try different job categories
- Check if job sites are accessible in your region

#### 4. Resume Upload Fails
- Ensure file is PDF, DOCX, or TXT
- Check file size (max 10MB)
- Verify file is not corrupted
- Try different file format

#### 5. Streamlit App Won't Start
```bash
# Check if port is available
netstat -an | grep 8501

# Try different port
streamlit run app.py --server.port 8502
```

### Performance Issues

#### Slow Response Times
1. **Check Internet Speed**: JobSpy requires stable connection
2. **Reduce Job Count**: Lower max_results in job search
3. **Clear Cache**: Delete `__pycache__` folders
4. **Restart App**: Close and reopen Streamlit

#### Memory Usage
- Monitor with `Task Manager` (Windows) or `Activity Monitor` (Mac)
- Expected usage: 500MB-1GB during operation
- Restart app if memory usage exceeds 2GB

### Error Messages

#### "Rate limit exceeded"
- **Cause**: Too many API requests
- **Solution**: Wait 1 minute and try again
- **Prevention**: Reduce concurrent operations

#### "Invalid API key"
- **Cause**: Incorrect or missing API key
- **Solution**: Verify `.env` file configuration
- **Check**: API key format and quotas

#### "Connection timeout"
- **Cause**: Network issues or server downtime
- **Solution**: Check internet connection
- **Retry**: Wait 30 seconds and try again

## 🛠️ Development Setup

### For Contributors

#### 1. Development Dependencies
```bash
pip install -r requirements-dev.txt
```

#### 2. Pre-commit Hooks
```bash
pre-commit install
```

#### 3. Running Tests
```bash
pytest tests/
```

#### 4. Code Formatting
```bash
black .
isort .
flake8 .
```

### Project Structure
```
Auto Applyer/
├── app.py                 # Main Streamlit application
├── assets/               # Resume uploads and static files
├── reports/              # Generated reports
├── logs/                # Application logs
├── tests/               # Unit and integration tests
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
├── .gitignore          # Git ignore rules
├── TODO.md             # Project roadmap
└── SETUP.md            # This file
```

## 📊 Performance Monitoring

### Key Metrics to Monitor
- **Response Time**: Should be <5 seconds for most operations
- **Memory Usage**: Should stay below 2GB
- **API Calls**: Track daily usage to avoid limits
- **Error Rate**: Should be <5% for production use

### Monitoring Commands
```bash
# Check app performance
streamlit run app.py --server.runOnSave true

# Monitor logs
tail -f logs/app.log

# Check memory usage
ps aux | grep streamlit
```

## 🔐 Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables only
- Rotate keys regularly
- Monitor API usage for suspicious activity

### Data Privacy
- Resume data is processed locally
- No personal data is stored permanently
- Clear browser cache after use
- Review generated outputs before sharing

## 📞 Support

### Getting Help
1. **Check this guide first**
2. **Review TODO.md** for known issues
3. **Search existing issues** on GitHub
4. **Create new issue** with:
   - Operating system
   - Python version
   - Error messages
   - Steps to reproduce

### Contact Information
- **GitHub Issues**: https://github.com/mooncakeSG/JobScryper-/issues
- **Email**: [Your contact email]
- **LinkedIn**: [Your LinkedIn profile]

## 🎉 Success Checklist

After setup, verify everything works:
- [ ] ✅ Streamlit app loads at localhost:8501
- [ ] ✅ Resume upload and parsing works
- [ ] ✅ Job search returns results
- [ ] ✅ AI resume suggestions generate
- [ ] ✅ Reports can be downloaded
- [ ] ✅ No error messages in console

**You're ready to find your dream job! 🚀**

---

*Last updated: [Current Date]*
*Version: 1.0* 