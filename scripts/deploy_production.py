#!/usr/bin/env python3
"""
Auto Applyer - Production Deployment Script

This script handles the complete production deployment process
including SQLite Cloud setup, database initialization, and application deployment.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logging_config import get_logger

logger = get_logger(__name__)


def run_command(command, description, check=True):
    """Run a shell command with error handling."""
    print(f"🔄 {description}...")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if Docker is installed
    if not run_command("docker --version", "Checking Docker installation", check=False):
        print("❌ Docker is not installed or not accessible")
        return False
    
    # Check if Docker Compose is installed
    if not run_command("docker-compose --version", "Checking Docker Compose installation", check=False):
        print("❌ Docker Compose is not installed or not accessible")
        return False
    
    # Check if .env.production exists
    env_file = Path(".env.production")
    if not env_file.exists():
        print("❌ .env.production file not found")
        print("   Please copy production.env.example to .env.production and configure it")
        return False
    
    # Check if required environment variables are set
    required_vars = [
        'SQLITE_CLOUD_HOST',
        'SQLITE_CLOUD_API_KEY',
        'SQLITE_CLOUD_DATABASE',
        'GROQ_API_KEY',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All prerequisites met")
    return True


def validate_sqlite_cloud():
    """Validate SQLite Cloud configuration."""
    print("🔍 Validating SQLite Cloud configuration...")
    
    if not run_command(
        "python scripts/validate_sqlite_cloud.py", 
        "Validating SQLite Cloud setup"
    ):
        print("❌ SQLite Cloud validation failed")
        return False
    
    return True


def build_docker_images():
    """Build Docker images for production."""
    print("🏗️ Building Docker images...")
    
    # Build backend image
    if not run_command(
        "docker-compose -f docker-compose.production.yml build backend",
        "Building backend image"
    ):
        return False
    
    # Build frontend image
    if not run_command(
        "docker-compose -f docker-compose.production.yml build frontend",
        "Building frontend image"
    ):
        return False
    
    return True


def deploy_application():
    """Deploy the application using Docker Compose."""
    print("🚀 Deploying application...")
    
    # Start services
    if not run_command(
        "docker-compose -f docker-compose.production.yml up -d",
        "Starting application services"
    ):
        return False
    
    # Wait for services to be healthy
    print("⏳ Waiting for services to be healthy...")
    import time
    time.sleep(30)
    
    # Check service status
    if not run_command(
        "docker-compose -f docker-compose.production.yml ps",
        "Checking service status"
    ):
        return False
    
    return True


def initialize_database():
    """Initialize the production database."""
    print("🗄️ Initializing production database...")
    
    # Initialize database
    if not run_command(
        "docker-compose -f docker-compose.production.yml exec backend python database/init_db.py --environment production",
        "Initializing database"
    ):
        return False
    
    # Run migrations
    if not run_command(
        "docker-compose -f docker-compose.production.yml exec backend python database/migrations.py --environment production",
        "Running database migrations"
    ):
        return False
    
    return True


def run_health_checks():
    """Run health checks on deployed services."""
    print("🏥 Running health checks...")
    
    # Check backend health
    if not run_command(
        "curl -f http://localhost:8000/health",
        "Checking backend health"
    ):
        return False
    
    # Check frontend health
    if not run_command(
        "curl -f http://localhost:3000",
        "Checking frontend health"
    ):
        return False
    
    return True


def setup_monitoring():
    """Set up basic monitoring."""
    print("📊 Setting up monitoring...")
    
    # Create monitoring directory
    Path("monitoring").mkdir(exist_ok=True)
    
    # Create basic monitoring script
    monitoring_script = """#!/bin/bash
# Basic monitoring script for Auto Applyer

echo "=== Auto Applyer Health Check ==="
echo "Timestamp: $(date)"
echo

# Check backend
echo "Backend Status:"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
fi

# Check frontend
echo "Frontend Status:"
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is down"
fi

# Check database
echo "Database Status:"
if docker-compose -f docker-compose.production.yml exec backend python -c "
from database.connection import get_database_manager
db = get_database_manager()
info = db.get_database_info()
print('Connected' if info['status'] == 'connected' else 'Disconnected')
" 2>/dev/null | grep -q "Connected"; then
    echo "✅ Database is connected"
else
    echo "❌ Database connection failed"
fi

echo
"""
    
    with open("monitoring/health_check.sh", "w") as f:
        f.write(monitoring_script)
    
    # Make script executable
    os.chmod("monitoring/health_check.sh", 0o755)
    
    print("✅ Monitoring setup completed")
    return True


def generate_deployment_report():
    """Generate deployment report."""
    print("📋 Generating deployment report...")
    
    report = f"""
# Auto Applyer Production Deployment Report

## Deployment Information
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Environment**: Production
- **Database**: SQLite Cloud
- **Frontend**: Next.js (Port 3000)
- **Backend**: FastAPI (Port 8000)

## Services Status
"""
    
    # Get service status
    try:
        result = subprocess.run(
            "docker-compose -f docker-compose.production.yml ps",
            shell=True, capture_output=True, text=True
        )
        report += f"\n```\n{result.stdout}\n```\n"
    except:
        report += "\nUnable to get service status\n"
    
    report += f"""
## Access Information
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Monitoring
- **Health Check Script**: monitoring/health_check.sh
- **Logs**: docker-compose -f docker-compose.production.yml logs

## Next Steps
1. Configure your domain and SSL certificates
2. Set up automated backups
3. Configure monitoring and alerting
4. Set up CI/CD pipeline

## Support
- **Documentation**: SQLITE_CLOUD_SETUP.md
- **Troubleshooting**: Check logs with 'docker-compose logs'
"""
    
    with open("deployment_report.md", "w") as f:
        f.write(report)
    
    print("✅ Deployment report generated: deployment_report.md")
    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy Auto Applyer to production')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip SQLite Cloud validation')
    parser.add_argument('--skip-monitoring', action='store_true',
                       help='Skip monitoring setup')
    parser.add_argument('--force', action='store_true',
                       help='Force deployment even if validation fails')
    
    args = parser.parse_args()
    
    print("🚀 Auto Applyer Production Deployment")
    print("="*50)
    
    # Load environment variables
    env_file = Path(".env.production")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Loaded environment from .env.production")
    else:
        print("⚠️  .env.production file not found")
    
    # Check prerequisites
    if not check_prerequisites():
        if not args.force:
            print("❌ Prerequisites check failed. Use --force to continue anyway.")
            sys.exit(1)
        else:
            print("⚠️  Continuing despite failed prerequisites...")
    
    # Validate SQLite Cloud
    if not args.skip_validation:
        if not validate_sqlite_cloud():
            if not args.force:
                print("❌ SQLite Cloud validation failed. Use --force to continue anyway.")
                sys.exit(1)
            else:
                print("⚠️  Continuing despite failed validation...")
    
    # Build images
    if not build_docker_images():
        print("❌ Docker image build failed")
        sys.exit(1)
    
    # Deploy application
    if not deploy_application():
        print("❌ Application deployment failed")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Database initialization failed")
        sys.exit(1)
    
    # Run health checks
    if not run_health_checks():
        print("❌ Health checks failed")
        sys.exit(1)
    
    # Setup monitoring
    if not args.skip_monitoring:
        setup_monitoring()
    
    # Generate report
    generate_deployment_report()
    
    print("\n🎉 Production deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Access your application at http://localhost:3000")
    print("2. Check the deployment report: deployment_report.md")
    print("3. Set up monitoring: monitoring/health_check.sh")
    print("4. Configure your domain and SSL certificates")


if __name__ == "__main__":
    main() 