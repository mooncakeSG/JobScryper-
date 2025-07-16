#!/bin/bash

echo "🚀 Setting up Complete Authentication System for JobScryper"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    print_error "Please run this script from the Auto Applyer directory"
    exit 1
fi

print_status "Installing backend dependencies..."

# Install Python dependencies
cd backend
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_success "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

cd ..

print_status "Installing frontend dependencies..."

# Install Node.js dependencies
cd job-frontend
npm install
if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Install Playwright browsers
print_status "Installing Playwright browsers..."
npx playwright install --with-deps
if [ $? -eq 0 ]; then
    print_success "Playwright browsers installed"
else
    print_warning "Failed to install Playwright browsers"
fi

cd ..

print_status "Setting up environment variables..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env 2>/dev/null || {
        print_warning "No .env.example found, creating basic .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./data/auto_applyer.db

# Authentication
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@yourapp.com

# API Keys
GROQ_API_KEY=your_groq_api_key

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    }
    print_success "Environment file created"
else
    print_warning ".env file already exists"
fi

print_status "Setting up database..."

# Create data directory if it doesn't exist
mkdir -p data

# Run database initialization
cd backend
python -c "
from database.init_db import init_database
init_database()
print('Database initialized successfully')
" 2>/dev/null || {
    print_warning "Database initialization failed, but continuing..."
}

cd ..

print_status "Running tests..."

# Run backend tests
print_status "Running backend tests..."
cd backend
python -m pytest tests/ -v --tb=short 2>/dev/null || {
    print_warning "Some backend tests failed, but continuing..."
}
cd ..

# Run frontend tests
print_status "Running frontend tests..."
cd job-frontend
npm run test 2>/dev/null || {
    print_warning "Some frontend tests failed, but continuing..."
}
cd ..

print_success "🎉 Authentication system setup complete!"

echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with your actual configuration"
echo "2. Start the backend: cd backend && python -m uvicorn main:app --reload"
echo "3. Start the frontend: cd job-frontend && npm run dev"
echo "4. Visit http://localhost:3000/auth/login to test the authentication"
echo ""
echo "🔧 Configuration needed:"
echo "- Set up email SMTP credentials for password reset"
echo "- Configure OAuth providers (Google, GitHub) if needed"
echo "- Set up your API keys for job search services"
echo ""
echo "📚 Documentation:"
echo "- Backend API: http://localhost:8000/docs"
echo "- Frontend: http://localhost:3000"
echo ""
echo "🧪 Testing:"
echo "- Run E2E tests: cd job-frontend && npm run test:e2e"
echo "- Run all tests: cd job-frontend && npm run test" 