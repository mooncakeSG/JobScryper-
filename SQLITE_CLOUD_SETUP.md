# SQLite Cloud Setup Guide

This guide will help you set up SQLite Cloud from sqlitecloud.io for production deployment of your Auto Applyer application.

## 🚀 What is SQLite Cloud?

SQLite Cloud is a managed SQLite service that provides:
- **High Availability**: 99.9% uptime SLA
- **Scalability**: Automatic scaling and load balancing
- **Security**: SSL/TLS encryption, authentication, and access controls
- **Backup**: Automated daily backups with point-in-time recovery
- **Monitoring**: Built-in performance monitoring and alerting
- **Global Distribution**: Multi-region deployment options

## 📋 Prerequisites

1. **SQLite Cloud Account**: Sign up at [sqlitecloud.io](https://sqlitecloud.io)
2. **Python Dependencies**: Install the SQLite Cloud Python driver
3. **Environment Variables**: Configure your production environment

## 🔧 Installation

### 1. SQLite Cloud Account Setup

1. **Create Account**: Visit [sqlitecloud.io](https://sqlitecloud.io) and sign up
2. **Get API Key**: 
   - Navigate to your dashboard
   - Go to API Keys section
   - Generate a new API key
   - Copy the API key (you'll need this for configuration)

### 2. Quick Setup (Recommended)

Use our automated setup script:

```bash
python scripts/setup_sqlite_cloud.py
```

This will:
- Prompt for your API key
- Create the database in SQLite Cloud
- Set up local database
- Sync data between local and cloud
- Create production environment file

## ⚙️ Environment Configuration

### Production Environment Variables

The setup script will automatically create a `.env.production` file, or you can create it manually:

```env
# SQLite Cloud Configuration
ENVIRONMENT=production
SQLITE_CLOUD_API_KEY=your_sqlite_cloud_api_key_here
SQLITE_CLOUD_DATABASE=auto_applyer
SQLITE_CLOUD_REGION=us-east-1

# Database Pool Configuration
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_RECYCLE=3600
DATABASE_TIMEOUT=30

# Application Configuration
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
LOG_LEVEL=INFO
```

### Docker Environment

Update your `docker-compose.yml` for production:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: auto-applyer-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SQLITE_CLOUD_HOST=${SQLITE_CLOUD_HOST}
      - SQLITE_CLOUD_PORT=${SQLITE_CLOUD_PORT}
      - SQLITE_CLOUD_DATABASE=${SQLITE_CLOUD_DATABASE}
      - SQLITE_CLOUD_USERNAME=${SQLITE_CLOUD_USERNAME}
      - SQLITE_CLOUD_PASSWORD=${SQLITE_CLOUD_PASSWORD}
      - SQLITE_CLOUD_SSL_MODE=${SQLITE_CLOUD_SSL_MODE}
      - DATABASE_POOL_SIZE=${DATABASE_POOL_SIZE}
      - DATABASE_MAX_OVERFLOW=${DATABASE_MAX_OVERFLOW}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    networks:
      - auto-applyer-network
    restart: unless-stopped

  frontend:
    build:
      context: ./job-frontend
      dockerfile: Dockerfile
    container_name: auto-applyer-frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - auto-applyer-network
    restart: unless-stopped

networks:
  auto-applyer-network:
    driver: bridge
```

## 🗄️ Database Initialization

### 1. Initialize Production Database

```bash
# Set environment to production
export ENVIRONMENT=production

# Initialize database with SQLite Cloud
python database/init_db.py --environment production
```

### 2. Run Migrations

```bash
# Run database migrations
python database/migrations.py --environment production
```

### 3. Verify Connection

```bash
# Test database connection
python -c "
from database.connection import init_database
db = init_database('production')
info = db.get_database_info()
print(f'Database Status: {info[\"status\"]}')
print(f'Database Type: {info[\"database_type\"]}')
print(f'Table Count: {info[\"table_count\"]}')
"
```

## 🔒 Security Configuration

### 1. SSL/TLS Configuration

SQLite Cloud requires SSL connections. The configuration automatically handles:
- SSL certificate verification
- Encrypted data transmission
- Secure authentication

### 2. Access Control

Configure database access:
- **IP Whitelist**: Restrict access to your application servers
- **User Permissions**: Use least-privilege access
- **Connection Limits**: Set appropriate pool sizes

### 3. Environment Security

```bash
# Secure environment variable handling
export SQLITE_CLOUD_PASSWORD=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -base64 64)
```

## 📊 Monitoring & Backup

### 1. SQLite Cloud Dashboard

Monitor your database through the SQLite Cloud dashboard:
- **Performance Metrics**: Query performance, connection counts
- **Storage Usage**: Database size and growth trends
- **Error Logs**: Connection errors and query failures
- **Backup Status**: Automated backup completion status

### 2. Application Monitoring

Add monitoring to your application:

```python
# In your main application
from database.connection import get_database_manager
import logging

logger = logging.getLogger(__name__)

def health_check():
    """Database health check for monitoring."""
    try:
        db_manager = get_database_manager()
        info = db_manager.get_database_info()
        
        if info["status"] == "connected":
            logger.info(f"Database healthy: {info['database_type']}")
            return True
        else:
            logger.error(f"Database unhealthy: {info}")
            return False
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
```

### 3. Backup Strategy

SQLite Cloud provides:
- **Automated Daily Backups**: Point-in-time recovery
- **Manual Backups**: On-demand backup creation
- **Cross-Region Replication**: Geographic redundancy

## 🚀 Deployment Steps

### 1. Production Deployment

```bash
# 1. Set production environment
export ENVIRONMENT=production

# 2. Build and deploy with Docker
docker-compose -f docker-compose.yml up --build -d

# 3. Initialize database
docker-compose exec backend python database/init_db.py --environment production

# 4. Run migrations
docker-compose exec backend python database/migrations.py --environment production

# 5. Verify deployment
docker-compose ps
curl http://localhost:8000/health
```

### 2. Environment Validation

```bash
# Validate environment configuration
python scripts/validate_env.py --environment production
```

### 3. Performance Testing

```bash
# Run performance tests
python tests/performance/test_database_performance.py --environment production
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Timeout
```
Error: Database connection test failed: timeout
```
**Solution**: Check network connectivity and firewall rules

#### 2. SSL Certificate Issues
```
Error: SSL certificate verification failed
```
**Solution**: Verify SSL configuration and certificate validity

#### 3. Authentication Failed
```
Error: Authentication failed for user
```
**Solution**: Verify username/password and user permissions

#### 4. Pool Exhaustion
```
Error: QueuePool limit of size X overflow Y reached
```
**Solution**: Increase pool size or optimize connection usage

### Debug Commands

```bash
# Test connection manually
python -c "
import os
from database.connection import DatabaseConfig
config = DatabaseConfig('production')
print(f'Database URL: {config.config[\"database_url\"]}')
"

# Check database status
python -c "
from database.connection import get_database_manager
db = get_database_manager()
print(db.get_database_info())
"
```

## 📈 Performance Optimization

### 1. Connection Pooling

Optimize connection pool settings:
```env
DATABASE_POOL_SIZE=10        # Base pool size
DATABASE_MAX_OVERFLOW=20     # Maximum overflow connections
DATABASE_POOL_RECYCLE=3600   # Recycle connections every hour
```

### 2. Query Optimization

- Use indexes for frequently queried columns
- Implement query caching where appropriate
- Monitor slow queries through SQLite Cloud dashboard

### 3. Application Optimization

- Use connection pooling effectively
- Implement proper error handling and retries
- Monitor application performance metrics

## 🔄 Migration from Development

### 1. Data Migration

If migrating from development SQLite:

```bash
# Export development data
python database/utilities.py --export data/development_export.json

# Import to production
python database/utilities.py --import data/development_export.json --environment production
```

### 2. Configuration Migration

Update configuration files:
- Environment variables
- Docker compose files
- Application settings

### 3. Testing Migration

```bash
# Test production setup
python tests/integration/test_production_setup.py
```

## 📞 Support

- **SQLite Cloud Support**: [support.sqlitecloud.io](https://support.sqlitecloud.io)
- **Documentation**: [docs.sqlitecloud.io](https://docs.sqlitecloud.io)
- **Community**: [community.sqlitecloud.io](https://community.sqlitecloud.io)

## 🎯 Next Steps

1. **Set up monitoring**: Configure application and database monitoring
2. **Implement backup strategy**: Test backup and restore procedures
3. **Performance tuning**: Optimize based on usage patterns
4. **Security audit**: Review and enhance security measures
5. **Documentation**: Update deployment and maintenance documentation 