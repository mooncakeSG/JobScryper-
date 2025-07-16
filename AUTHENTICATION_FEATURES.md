# Auto Applyer - Enhanced Authentication Features

## Overview

Auto Applyer now supports comprehensive authentication features including Two-Factor Authentication (2FA), social login, email verification, and enhanced security measures.

## 🔐 Two-Factor Authentication (2FA)

### Features
- **TOTP-based 2FA** using Google Authenticator, Authy, or any TOTP app
- **QR Code generation** for easy setup
- **Backup codes** for account recovery
- **Manual entry codes** for devices without cameras
- **Enable/Disable 2FA** with verification

### Setup Process
1. User navigates to Settings → Security
2. Clicks "Setup Two-Factor Authentication"
3. Scans QR code with authenticator app
4. Enters verification code to enable 2FA
5. Receives backup codes for safekeeping

### API Endpoints
```bash
# Setup 2FA
POST /api/auth/setup-2fa

# Enable 2FA
POST /api/auth/enable-2fa
{
  "code": "123456"
}

# Disable 2FA
POST /api/auth/disable-2fa
{
  "code": "123456"
}
```

### Database Schema
```sql
-- 2FA fields in users table
ALTER TABLE users ADD COLUMN two_fa_secret TEXT;
ALTER TABLE users ADD COLUMN two_fa_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN backup_codes TEXT;
```

## 🌐 Social Login

### Supported Providers
- **Google OAuth 2.0**
- **GitHub OAuth**

### Features
- **Seamless signup/login** with social accounts
- **Automatic account creation** for new users
- **Profile picture import** from social accounts
- **Email verification bypass** for verified social accounts

### Setup Requirements
```bash
# Environment variables
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### API Endpoints
```bash
# Social login
POST /api/auth/social-login
{
  "provider": "google|github",
  "token": "oauth_token"
}
```

### Database Schema
```sql
-- Social login fields in users table
ALTER TABLE users ADD COLUMN social_provider TEXT;
ALTER TABLE users ADD COLUMN social_id TEXT;
ALTER TABLE users ADD COLUMN profile_picture TEXT;

-- Social providers table
CREATE TABLE social_providers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  client_id TEXT NOT NULL,
  client_secret TEXT NOT NULL,
  auth_url TEXT NOT NULL,
  token_url TEXT NOT NULL,
  userinfo_url TEXT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);
```

## 📧 Email Verification

### Features
- **6-digit verification codes** sent via email
- **10-minute expiration** for security
- **Resend functionality** with cooldown
- **HTML email templates** with branding
- **Automatic verification** for social logins

### Email Template
```html
<h2>Welcome to Auto Applyer!</h2>
<p>Hi {username},</p>
<p>Please verify your email address by entering this code:</p>
<h1 style="color: #007bff; font-size: 32px; text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">{code}</h1>
<p>This code will expire in 10 minutes.</p>
```

### API Endpoints
```bash
# Verify email
POST /api/auth/verify-email
{
  "email": "user@example.com",
  "code": "123456"
}

# Resend verification
POST /api/auth/resend-verification
{
  "email": "user@example.com"
}
```

### Database Schema
```sql
-- Email verification fields
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verification_code TEXT;
ALTER TABLE users ADD COLUMN email_verification_expires DATETIME;
```

## 🔑 Password Management

### Features
- **Bcrypt password hashing** for enhanced security
- **SHA-256 fallback** for existing users
- **Password reset tokens** with expiration
- **Password change tracking**
- **Failed login attempt monitoring**

### Password Reset Flow
1. User requests password reset
2. System generates secure token
3. Reset link sent via email
4. User clicks link and sets new password
5. Token marked as used

### API Endpoints
```bash
# Request password reset
POST /api/auth/forgot-password
{
  "email": "user@example.com"
}

# Reset password
POST /api/auth/reset-password
{
  "token": "reset_token",
  "new_password": "new_password"
}
```

### Database Schema
```sql
-- Password reset tokens
CREATE TABLE password_reset_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token_hash TEXT NOT NULL,
  expires_at DATETIME NOT NULL,
  used_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Security fields
ALTER TABLE users ADD COLUMN password_changed_at DATETIME;
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN account_locked_until DATETIME;
ALTER TABLE users ADD COLUMN last_login DATETIME;
```

## 🔄 Token Management

### Features
- **JWT access tokens** with 60-minute expiration
- **Refresh tokens** with 30-day expiration
- **Token refresh endpoint** for seamless sessions
- **Token revocation** support

### API Endpoints
```bash
# Refresh token
POST /api/auth/refresh-token
{
  "refresh_token": "refresh_token"
}
```

### Database Schema
```sql
-- Refresh tokens
CREATE TABLE refresh_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token_hash TEXT NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_revoked BOOLEAN DEFAULT FALSE
);
```

## 📱 Session Management

### Features
- **Multi-device sessions** tracking
- **Device information** logging
- **IP address tracking** for security
- **Session expiration** management
- **Active session listing**

### Database Schema
```sql
-- Login sessions
CREATE TABLE login_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  session_token TEXT NOT NULL,
  device_info TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);
```

## 📊 Security Events

### Features
- **Comprehensive audit logging** of security events
- **Failed login tracking** with IP addresses
- **Suspicious activity detection**
- **Security event history** for users

### Event Types
- Login attempts (successful/failed)
- Password changes
- 2FA setup/enable/disable
- Email verification
- Social login
- Password reset requests

### Database Schema
```sql
-- Security events
CREATE TABLE security_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  event_data TEXT,
  ip_address TEXT,
  user_agent TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🛡️ Security Features

### Password Security
- **Bcrypt hashing** with salt
- **Minimum password requirements** (configurable)
- **Password strength validation**
- **Common password blocking**

### Account Protection
- **Failed login attempt limiting**
- **Account lockout** after multiple failures
- **IP-based rate limiting**
- **Suspicious activity monitoring**

### Session Security
- **Secure token generation**
- **Token expiration** enforcement
- **Session invalidation** on password change
- **Concurrent session management**

## 🔧 Configuration

### Environment Variables
```bash
# JWT Configuration
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Social Login
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# 2FA Configuration
TOTP_ISSUER=Auto Applyer
TOTP_DIGITS=6
TOTP_PERIOD=30
```

### Dependencies
```bash
# Install required packages
pip install pyotp qrcode[pil] cryptography bcrypt passlib python-multipart
pip install authlib httpx fastapi-mail jinja2
```

## 🧪 Testing

### Playwright Tests
Comprehensive test suite covering:
- 2FA setup and verification
- Social login flows
- Email verification
- Password reset
- Form validation
- Error handling
- Mobile responsiveness

### Test Commands
```bash
# Run all auth tests
npx playwright test auth-enhanced.spec.ts

# Run specific test
npx playwright test --grep "2FA"

# Run with UI
npx playwright test --ui
```

## 🚀 Deployment

### Production Checklist
- [ ] Set secure `SECRET_KEY`
- [ ] Configure SMTP settings
- [ ] Set up social OAuth apps
- [ ] Enable HTTPS
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Test all flows
- [ ] Backup database

### Security Best Practices
- Use strong, unique passwords
- Enable 2FA for all accounts
- Regularly rotate secrets
- Monitor security events
- Keep dependencies updated
- Use HTTPS everywhere
- Implement rate limiting

## 📚 API Reference

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | User registration |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/social-login` | Social login |
| POST | `/api/auth/verify-email` | Email verification |
| POST | `/api/auth/resend-verification` | Resend verification |
| POST | `/api/auth/setup-2fa` | Setup 2FA |
| POST | `/api/auth/enable-2fa` | Enable 2FA |
| POST | `/api/auth/disable-2fa` | Disable 2FA |
| POST | `/api/auth/refresh-token` | Refresh token |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password |

### Response Formats
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": 123
}
```

## 🆘 Troubleshooting

### Common Issues
1. **2FA not working**: Check time synchronization
2. **Email not sending**: Verify SMTP settings
3. **Social login failing**: Check OAuth configuration
4. **Token expiration**: Use refresh token endpoint
5. **Database errors**: Check connection and migrations

### Debug Commands
```bash
# Check database tables
python -c "import sqlite3; conn = sqlite3.connect('test.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"

# Test email sending
python -c "from auth_enhanced import auth; print(auth.send_verification_email('test@example.com', '123456', 'testuser'))"

# Verify 2FA setup
python -c "import pyotp; totp = pyotp.TOTP('your_secret'); print(totp.now())"
```

## 📈 Future Enhancements

### Planned Features
- **Biometric authentication** (fingerprint, face ID)
- **Hardware security keys** (YubiKey, FIDO2)
- **Advanced threat detection**
- **Multi-factor authentication** (SMS, email)
- **Single Sign-On (SSO)** integration
- **OAuth 2.1** compliance
- **Zero-knowledge proofs**
- **Blockchain-based identity**

### Integration Possibilities
- **Active Directory** integration
- **LDAP** support
- **SAML** authentication
- **OIDC** providers
- **Enterprise SSO** solutions

---

For more information, see the [API Reference](API_REFERENCE.md) and [Security Guide](SECURITY_GUIDE.md). 