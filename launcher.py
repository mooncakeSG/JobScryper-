#!/usr/bin/env python3
"""
Auto Applyer Launcher

Choose between the current app and the enhanced version with modern UI.
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path

st.set_page_config(
    page_title="Auto Applyer Launcher",
    page_icon="🚀",
    layout="centered"
)

def install_ui_requirements():
    """Install additional UI requirements."""
    ui_req_path = Path("ui/requirements.txt")
    if ui_req_path.exists():
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(ui_req_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                st.success("✅ UI requirements installed successfully!")
                return True
            else:
                st.error(f"❌ Failed to install UI requirements: {result.stderr}")
                return False
        except Exception as e:
            st.error(f"❌ Error installing UI requirements: {e}")
            return False
    else:
        st.warning("⚠️ UI requirements file not found")
        return False

def check_database_status():
    """Check if database is initialized."""
    db_path = Path("data/auto_applyer.db")
    if db_path.exists():
        return True, f"Database found ({db_path.stat().st_size / 1024:.1f} KB)"
    else:
        return False, "Database not initialized"

def main():
    """Main launcher interface."""
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🚀 Auto Applyer</h1>
        <p style='font-size: 1.2rem; color: #666;'>Choose your experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check system status
    st.markdown("### 📊 System Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        db_exists, db_status = check_database_status()
        status_icon = "✅" if db_exists else "❌"
        st.markdown(f"**Database:** {status_icon} {db_status}")
    
    with col2:
        ui_deps = Path("ui/requirements.txt").exists()
        ui_icon = "✅" if ui_deps else "❌"
        st.markdown(f"**UI Components:** {ui_icon} {'Available' if ui_deps else 'Not installed'}")
    
    st.markdown("---")
    
    # App selection
    st.markdown("### 🎯 Choose Your Version")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            background: #f9f9f9;
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <h3>📱 Current App</h3>
            <p>The existing Auto Applyer with all current features</p>
            <ul style='text-align: left; margin: 1rem 0;'>
                <li>Job search across multiple sources</li>
                <li>Resume analysis and AI suggestions</li>
                <li>Application tracking (CSV)</li>
                <li>Interview preparation tips</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch Current App", use_container_width=True):
            st.balloons()
            st.success("🎉 Launching current app...")
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=os.getcwd())
    
    with col2:
        st.markdown("""
        <div style='
            border: 1px solid #2563eb;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <h3>✨ Enhanced App</h3>
            <p>Modern UI with database integration</p>
            <ul style='text-align: left; margin: 1rem 0;'>
                <li>User profiles and authentication</li>
                <li>Database-backed application tracking</li>
                <li>Advanced analytics and charts</li>
                <li>Modern, responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        enhanced_ready = db_exists and ui_deps
        
        if enhanced_ready:
            if st.button("🌟 Launch Enhanced App", use_container_width=True):
                st.balloons()
                st.success("🎉 Launching enhanced app...")
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app_enhanced.py"], cwd=os.getcwd())
        else:
            st.markdown("**Setup Required:**")
            
            if not db_exists:
                if st.button("🗄️ Initialize Database", use_container_width=True):
                    with st.spinner("Initializing database..."):
                        try:
                            subprocess.run([sys.executable, "database/init_db.py"], cwd=os.getcwd())
                            st.success("✅ Database initialized!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Database initialization failed: {e}")
            
            if not ui_deps:
                if st.button("📦 Install UI Requirements", use_container_width=True):
                    with st.spinner("Installing UI requirements..."):
                        if install_ui_requirements():
                            st.rerun()
    
    st.markdown("---")
    
    # Quick setup
    st.markdown("### ⚡ Quick Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 Complete Setup", use_container_width=True):
            with st.spinner("Setting up Auto Applyer..."):
                success = True
                
                # Install UI requirements
                if not ui_deps:
                    st.info("Installing UI requirements...")
                    success = install_ui_requirements()
                
                # Initialize database
                if success and not db_exists:
                    st.info("Initializing database...")
                    try:
                        subprocess.run([sys.executable, "database/init_db.py"], cwd=os.getcwd())
                        st.success("✅ Database initialized!")
                    except Exception as e:
                        st.error(f"❌ Database initialization failed: {e}")
                        success = False
                
                if success:
                    st.success("🎉 Setup completed! You can now use the enhanced app.")
                    st.rerun()
    
    with col2:
        if st.button("📚 View Documentation", use_container_width=True):
            st.markdown("""
            ### 📖 Documentation
            
            **Current App Features:**
            - Multi-source job search (JobSpy, Alternative APIs)
            - Resume upload and parsing
            - AI-powered job matching
            - ATS compliance analysis
            - Interview preparation tips
            - CSV-based application tracking
            
            **Enhanced App Features:**
            - Everything from current app
            - User authentication and profiles
            - Database-backed data persistence
            - Advanced analytics and visualization
            - Modern, responsive UI design
            - Enhanced search and filtering
            - Real-time notifications
            - Export functionality (CSV, Excel, JSON)
            
            **Requirements:**
            - Python 3.8+
            - All dependencies in requirements.txt
            - Optional: Additional UI dependencies for enhanced version
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem 0;'>
        <p>JOBscryper- Your AI-Powered Job Application Assistant</p>
        <p>Built using Streamlit, SQLAlchemy, and modern web technologies</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 