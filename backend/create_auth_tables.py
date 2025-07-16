"""
Database migrations for enhanced authentication features
Creates tables for 2FA, social login, email verification, and security features
"""

import sqlite3
from datetime import datetime

def create_auth_tables():
    """Create all authentication-related tables"""
    
    # Connect to database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # 1. Add 2FA fields to users table
        print("🔐 Adding 2FA fields to users table...")
        cursor.execute("""
            ALTER TABLE users ADD COLUMN two_fa_secret TEXT;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN two_fa_enabled BOOLEAN DEFAULT FALSE;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN backup_codes TEXT;
        """)
        
        # 2. Add social login fields to users table
        print("🔗 Adding social login fields to users table...")
        cursor.execute("""
            ALTER TABLE users ADD COLUMN social_provider TEXT;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN social_id TEXT;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN profile_picture TEXT;
        """)
        
        # 3. Add email verification fields to users table
        print("📧 Adding email verification fields to users table...")
        cursor.execute("""
            ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN email_verification_code TEXT;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN email_verification_expires DATETIME;
        """)
        
        # 4. Add security fields to users table
        print("🔒 Adding security fields to users table...")
        cursor.execute("""
            ALTER TABLE users ADD COLUMN password_changed_at DATETIME;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN account_locked_until DATETIME;
        """)
        cursor.execute("""
            ALTER TABLE users ADD COLUMN last_login DATETIME;
        """)
        
        # 5. Create refresh tokens table
        print("🔄 Creating refresh tokens table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_revoked BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # 6. Create login sessions table
        print("📱 Creating login sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # 7. Create password reset tokens table
        print("🔑 Creating password reset tokens table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                used_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # 8. Create security events table
        print("📊 Creating security events table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        
        # 9. Create social login providers table
        print("🌐 Creating social login providers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS social_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                client_id TEXT NOT NULL,
                client_secret TEXT NOT NULL,
                auth_url TEXT NOT NULL,
                token_url TEXT NOT NULL,
                userinfo_url TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 10. Insert default social providers
        print("➕ Inserting default social providers...")
        providers = [
            ("google", "google_client_id", "google_client_secret", 
             "https://accounts.google.com/o/oauth2/auth",
             "https://oauth2.googleapis.com/token",
             "https://www.googleapis.com/oauth2/v2/userinfo"),
            ("github", "github_client_id", "github_client_secret",
             "https://github.com/login/oauth/authorize",
             "https://github.com/login/oauth/access_token",
             "https://api.github.com/user")
        ]
        
        for provider in providers:
            cursor.execute("""
                INSERT OR IGNORE INTO social_providers 
                (name, client_id, client_secret, auth_url, token_url, userinfo_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, provider)
        
        # 11. Create indexes for performance
        print("⚡ Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_sessions_user_id ON login_sessions(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_sessions_token ON login_sessions(session_token);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_password_reset_user_id ON password_reset_tokens(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON security_events(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_social_id ON users(social_id);")
        
        # Commit all changes
        conn.commit()
        print("✅ All authentication tables created successfully!")
        
        # Show summary
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%auth%' OR name LIKE '%social%' OR name LIKE '%token%' OR name LIKE '%session%' OR name LIKE '%security%'")
        tables = cursor.fetchall()
        print(f"📋 Created/updated {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
            
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("⚠️  Some columns already exist, continuing...")
        else:
            print(f"❌ Database error: {e}")
            conn.rollback()
    except Exception as e:
        print(f"❌ Error creating auth tables: {e}")
        conn.rollback()
    finally:
        conn.close()

def update_existing_users():
    """Update existing users with new authentication fields"""
    
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Update existing users to have email_verified = TRUE
        cursor.execute("""
            UPDATE users SET email_verified = TRUE WHERE email_verified IS NULL
        """)
        
        # Update existing users to have two_fa_enabled = FALSE
        cursor.execute("""
            UPDATE users SET two_fa_enabled = FALSE WHERE two_fa_enabled IS NULL
        """)
        
        # Update existing users to have failed_login_attempts = 0
        cursor.execute("""
            UPDATE users SET failed_login_attempts = 0 WHERE failed_login_attempts IS NULL
        """)
        
        conn.commit()
        print("✅ Updated existing users with default authentication values")
        
    except Exception as e:
        print(f"❌ Error updating existing users: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Setting up enhanced authentication database...")
    create_auth_tables()
    update_existing_users()
    print("🎉 Enhanced authentication setup complete!") 