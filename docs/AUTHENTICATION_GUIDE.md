# 🔐 Complete Authentication System Guide

## Overview

This guide covers the complete authentication system implemented for JobScryper, including user registration, login, password reset, email verification, and social login integration.

## 🏗️ Architecture

### Backend (FastAPI)
- **JWT-based authentication** with access and refresh tokens
- **Secure password hashing** using bcrypt
- **Email verification** and password reset flows
- **Social login** support (Google, GitHub)
- **Input validation** using Pydantic models
- **Database integration** with SQLite Cloud

### Frontend (Next.js)
- **React Hook Form** with Zod validation
- **Tailwind CSS** for styling
- **Context-based state management**
- **Responsive design** for mobile and desktop
- **E2E testing** with Playwright

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd Auto Applyer

# Run the setup script
chmod +x setup_auth.sh
./setup_auth.sh
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Authentication
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (for password reset)
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
GITHUB_CLIENT_ID=your_github_client_id
```

### 3. Start Services

```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend (in new terminal)
cd job-frontend
npm run dev
```

## 📋 Features

### ✅ User Registration
- Username and email validation
- Strong password requirements
- Email verification
- Welcome email

### ✅ User Login
- Username/email login
- Password visibility toggle
- Remember me functionality
- JWT token management

### ✅ Password Reset
- Secure token generation
- Email-based reset flow
- Token expiration
- Password strength validation

### ✅ Email Verification
- Email verification tokens
- Resend verification
- Account activation

### ✅ Social Login
- Google OAuth integration
- GitHub OAuth integration
- Account linking

### ✅ Security Features
- bcrypt password hashing
- JWT token rotation
- CSRF protection
- Rate limiting
- Input sanitization

## 🔧 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | User logout |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password with token |
| POST | `/api/auth/verify-email` | Verify email with token |
| POST | `/api/auth/resend-verification` | Resend verification email |
| GET | `/api/auth/me` | Get current user info |

### Request/Response Examples

#### Registration
```json
POST /api/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": 1
}
```

#### Login
```json
POST /api/auth/login
{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_verified": true
}
```

## 🎨 Frontend Components

### Login Page (`/auth/login`)
- Username/email input
- Password input with visibility toggle
- Social login buttons
- Forgot password link
- Sign up link

### Signup Page (`/auth/signup`)
- Username input with validation
- Email input with validation
- Password input with strength indicator
- Password confirmation
- Social signup buttons

### Forgot Password Page (`/auth/forgot-password`)
- Email input
- Success confirmation
- Back to login link

### Password Reset Page (`/auth/reset-password`)
- Token validation
- New password input
- Password confirmation

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd job-frontend
npm run test
```

### E2E Tests
```bash
cd job-frontend
npm run test:e2e
```

### Test Coverage
```bash
# Backend coverage
cd backend
python -m pytest tests/ --cov=. --cov-report=html

# Frontend coverage
cd job-frontend
npm run test -- --coverage
```

## 🔒 Security Best Practices

### Password Security
- Minimum 8 characters
- Require uppercase, lowercase, number
- bcrypt hashing with salt
- Password strength indicator

### Token Security
- JWT with short expiration
- Refresh token rotation
- Secure token storage
- HTTPS only in production

### Input Validation
- Server-side validation with Pydantic
- Client-side validation with Zod
- SQL injection prevention
- XSS protection

### Rate Limiting
- Login attempt limiting
- Password reset limiting
- API rate limiting

## 📱 Mobile Responsiveness

The authentication pages are fully responsive and optimized for:
- Mobile phones (320px+)
- Tablets (768px+)
- Desktop (1024px+)

## 🚀 Deployment

### Environment Variables
Set these in your production environment:

```bash
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-database-url

# Email settings
SMTP_SERVER=your-smtp-server
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password

# Frontend settings
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXTAUTH_URL=https://your-frontend-domain.com
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🔧 Customization

### Adding New OAuth Providers
1. Add provider configuration to `.env`
2. Update `auth_system.py` with provider logic
3. Add provider buttons to frontend
4. Update tests

### Custom Email Templates
1. Modify email templates in `auth_system.py`
2. Update HTML content
3. Test email delivery

### Custom Validation Rules
1. Update Pydantic models in `auth_system.py`
2. Update Zod schemas in frontend
3. Update tests

## 🐛 Troubleshooting

### Common Issues

#### Email Not Sending
- Check SMTP credentials
- Verify firewall settings
- Check email provider settings

#### Token Expiration
- Increase token expiration times
- Implement refresh token logic
- Check clock synchronization

#### Database Connection
- Verify database URL
- Check network connectivity
- Verify credentials

### Debug Mode
Enable debug mode for detailed logs:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Hook Form](https://react-hook-form.com/)
- [Zod Validation](https://zod.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Playwright Testing](https://playwright.dev/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 