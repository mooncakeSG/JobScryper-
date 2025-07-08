"""
Auto Applyer - UI Components

Reusable UI components for the enhanced Streamlit interface including
modern styling, responsive design, and interactive elements.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

def apply_modern_theme():
    """Apply modern theme and styling to the Streamlit app."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Custom CSS Variables */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #64748b;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --background-color: #f8fafc;
        --surface-color: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .app-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, #3b82f6 100%);
        color: white;
        padding: 2rem 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
        text-align: center;
        box-shadow: var(--shadow-lg);
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .app-header p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Card Styles */
    .metric-card {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Job Card Styles */
    .job-card {
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }
    
    .job-card:hover {
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .job-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        font-size: 1rem;
        color: var(--primary-color);
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .job-location {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
    }
    
    .job-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .job-tag {
        background: #f1f5f9;
        color: var(--text-secondary);
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Button Styles */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background: #1d4ed8;
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-applied { background: #dbeafe; color: #1e40af; }
    .status-interview { background: #fef3c7; color: #92400e; }
    .status-offered { background: #d1fae5; color: #065f46; }
    .status-rejected { background: #fee2e2; color: #991b1b; }
    .status-pending { background: #f3f4f6; color: #374151; }
    
    /* Navigation Styles */
    .nav-item {
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: var(--background-color);
    }
    
    .nav-item.active {
        background: var(--primary-color);
        color: white;
    }
    
    /* Form Styles */
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        padding: 0.75rem;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
    }
    
    /* Progress Styles */
    .progress-container {
        background: var(--background-color);
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, var(--primary-color) 0%, #3b82f6 100%);
        height: 0.5rem;
        border-radius: 0.25rem;
        transition: width 0.3s ease;
    }
    
    /* Alert Styles */
    .alert {
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background: #f0fdf4;
        border-color: var(--success-color);
        color: #14532d;
    }
    
    .alert-warning {
        background: #fffbeb;
        border-color: var(--warning-color);
        color: #92400e;
    }
    
    .alert-error {
        background: #fef2f2;
        border-color: var(--error-color);
        color: #991b1b;
    }
    
    .alert-info {
        background: #eff6ff;
        border-color: var(--primary-color);
        color: #1e40af;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .job-card {
            padding: 1rem;
        }
    }
    
    /* Dark Theme Support */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0f172a;
            --surface-color: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
        }
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background-color);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    </style>
    """, unsafe_allow_html=True)


def create_app_header(title: str, subtitle: str, user_name: Optional[str] = None):
    """Create a modern app header with user info."""
    user_info = f" | Welcome, {user_name}" if user_name else ""
    
    st.markdown(f"""
    <div class="app-header">
        <h1>🚀 {title}</h1>
        <p>{subtitle}{user_info}</p>
    </div>
    """, unsafe_allow_html=True)


def create_metric_card(label: str, value: str, delta: Optional[str] = None, icon: Optional[str] = None):
    """Create a metric card with optional delta and icon."""
    icon_html = f"<i class='{icon}' style='font-size: 1.5rem; margin-bottom: 0.5rem; color: var(--primary-color);'></i><br>" if icon else ""
    delta_html = f"<div style='font-size: 0.75rem; color: var(--success-color); margin-top: 0.25rem;'>{delta}</div>" if delta else ""
    
    st.markdown(f"""
    <div class="metric-card">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def create_job_card(job: Dict[str, Any], show_actions: bool = True, user_applied: bool = False):
    """Create a modern job card with actions."""
    
    # Extract job details
    title = job.get('title', 'Unknown Position')
    company = job.get('company', 'Unknown Company')
    location = job.get('location', 'Unknown Location')
    salary = job.get('salary', '')
    job_type = job.get('job_type', '')
    description = job.get('description', '')[:200] + "..." if len(job.get('description', '')) > 200 else job.get('description', '')
    posted_date = job.get('date_posted', '')
    source = job.get('source', 'Unknown')
    match_score = job.get('match_score', 0)
    
    # Create tags
    tags = []
    if job_type:
        tags.append(job_type)
    if salary:
        tags.append(salary)
    if source:
        tags.append(f"via {source}")
    
    tags_html = ''.join([f'<span class="job-tag">{tag}</span>' for tag in tags])
    
    # Match score indicator
    match_color = "#059669" if match_score >= 80 else "#d97706" if match_score >= 60 else "#64748b"
    match_html = f'<div style="color: {match_color}; font-weight: 500; font-size: 0.875rem;">Match: {match_score}%</div>' if match_score > 0 else ""
    
    # Application status
    status_html = ""
    if user_applied:
        status_html = '<span class="status-badge status-applied">Applied</span>'
    
    card_html = f"""
    <div class="job-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div style="flex: 1;">
                <div class="job-title">{title}</div>
                <div class="job-company">{company}</div>
                <div class="job-location">📍 {location}</div>
                {match_html}
            </div>
            <div style="text-align: right;">
                {status_html}
                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    {posted_date}
                </div>
            </div>
        </div>
        
        {f'<div style="margin-bottom: 1rem; color: var(--text-secondary); line-height: 1.5;">{description}</div>' if description else ''}
        
        <div class="job-tags">
            {tags_html}
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    if show_actions:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            if st.button("📄 View Details", key=f"view_{job.get('id', hash(str(job)))}", use_container_width=True):
                return "view_details"
        
        with col2:
            if st.button("🤖 AI Analysis", key=f"analyze_{job.get('id', hash(str(job)))}", use_container_width=True):
                return "analyze"
        
        with col3:
            apply_label = "✅ Applied" if user_applied else "📤 Apply"
            disabled = user_applied
            if st.button(apply_label, key=f"apply_{job.get('id', hash(str(job)))}", use_container_width=True, disabled=disabled):
                return "apply"
        
        with col4:
            if st.button("💾", key=f"save_{job.get('id', hash(str(job)))}", help="Save for later"):
                return "save"
    
    return None


def create_status_badge(status: str) -> str:
    """Create a status badge HTML."""
    status_classes = {
        'applied': 'status-applied',
        'interview_scheduled': 'status-interview', 
        'interviewed': 'status-interview',
        'offer_received': 'status-offered',
        'offer_accepted': 'status-offered',
        'rejected': 'status-rejected',
        'pending': 'status-pending'
    }
    
    status_class = status_classes.get(status.lower(), 'status-pending')
    display_status = status.replace('_', ' ').title()
    
    return f'<span class="status-badge {status_class}">{display_status}</span>'


def create_progress_bar(current: int, total: int, label: str = "") -> None:
    """Create a progress bar with label."""
    percentage = (current / total * 100) if total > 0 else 0
    
    st.markdown(f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 500;">{label}</span>
            <span style="color: var(--text-secondary);">{current}/{total} ({percentage:.1f}%)</span>
        </div>
        <div style="background: var(--border-color); border-radius: 0.25rem; height: 0.5rem;">
            <div class="progress-bar" style="width: {percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_alert(message: str, alert_type: str = "info", dismissible: bool = False) -> None:
    """Create an alert message."""
    icons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    icon = icons.get(alert_type, 'ℹ️')
    dismiss_btn = '<button style="float: right; background: none; border: none; font-size: 1.2rem; cursor: pointer;" onclick="this.parentElement.style.display=\'none\'">×</button>' if dismissible else ''
    
    st.markdown(f"""
    <div class="alert alert-{alert_type}">
        {dismiss_btn}
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)


def create_stats_chart(data: pd.DataFrame, chart_type: str, title: str, x_col: str, y_col: str) -> None:
    """Create interactive charts using Plotly."""
    
    if chart_type == "bar":
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col,
            title=title,
            color_discrete_sequence=['#2563eb']
        )
    elif chart_type == "line":
        fig = px.line(
            data,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=['#2563eb']
        )
    elif chart_type == "pie":
        fig = px.pie(
            data,
            values=y_col,
            names=x_col,
            title=title,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
    else:
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=['#2563eb']
        )
    
    # Update layout for better appearance
    fig.update_layout(
        font_family="Inter",
        title_font_size=16,
        title_font_color="#1e293b",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400
    )
    
    fig.update_xaxes(gridcolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#e2e8f0")
    
    st.plotly_chart(fig, use_container_width=True)


def create_sidebar_profile(user_data: Dict[str, Any]) -> None:
    """Create user profile section in sidebar."""
    if user_data:
        st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 1rem;
            border-radius: 0.75rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-weight: 600; font-size: 1.1rem;">{user_data.get('full_name', 'User')}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">{user_data.get('email', '')}</div>
            <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;">
                {user_data.get('job_title', 'Job Seeker')} • {user_data.get('location', 'Unknown')}
            </div>
        </div>
        """, unsafe_allow_html=True)


def create_notification_toast(message: str, notification_type: str = "info", duration: int = 3000) -> None:
    """Create a toast notification (requires custom JavaScript)."""
    colors = {
        'success': '#059669',
        'warning': '#d97706', 
        'error': '#dc2626',
        'info': '#2563eb'
    }
    
    color = colors.get(notification_type, colors['info'])
    
    st.markdown(f"""
    <script>
    setTimeout(function() {{
        const toast = document.createElement('div');
        toast.innerHTML = '{message}';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: {color};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            font-family: Inter, sans-serif;
            font-weight: 500;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {{
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }}, 100);
        
        setTimeout(() => {{
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => document.body.removeChild(toast), 300);
        }}, {duration});
    }}, 100);
    </script>
    """, unsafe_allow_html=True)


def create_data_table(data: List[Dict[str, Any]], columns: List[str], sortable: bool = True, 
                     searchable: bool = True, pagination: bool = True, page_size: int = 10) -> pd.DataFrame:
    """Create an enhanced data table with sorting, searching, and pagination."""
    
    if not data:
        st.info("No data to display")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Search functionality
    if searchable and not df.empty:
        search_term = st.text_input("🔍 Search", placeholder="Search in table...")
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df = df[mask]
    
    # Column selection
    if columns:
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
    
    # Sorting
    if sortable and not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_column = st.selectbox("Sort by", df.columns, key="sort_col")
        with col2:
            sort_order = st.selectbox("Order", ["Ascending", "Descending"], key="sort_order")
        
        ascending = sort_order == "Ascending"
        df = df.sort_values(sort_column, ascending=ascending)
    
    # Pagination
    if pagination and not df.empty:
        total_rows = len(df)
        total_pages = (total_rows - 1) // page_size + 1
        
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                page = st.selectbox(
                    f"Page (1-{total_pages})", 
                    range(1, total_pages + 1),
                    key="page_select"
                )
            
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            df_page = df.iloc[start_idx:end_idx]
            
            st.info(f"Showing {start_idx + 1}-{end_idx} of {total_rows} rows")
        else:
            df_page = df
    else:
        df_page = df
    
    # Display table
    if not df_page.empty:
        st.dataframe(df_page, use_container_width=True, hide_index=True)
    else:
        st.info("No results found")
    
    return df_page


def create_export_buttons(data: pd.DataFrame, filename_prefix: str = "export") -> None:
    """Create export buttons for different formats."""
    if data.empty:
        return
    
    col1, col2, col3 = st.columns(3)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with col1:
        csv_data = data.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"{filename_prefix}_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = data.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="📊 Download Excel", 
            data=excel_buffer,
            file_name=f"{filename_prefix}_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        json_data = data.to_json(orient='records', indent=2)
        st.download_button(
            label="⚙️ Download JSON",
            data=json_data,
            file_name=f"{filename_prefix}_{timestamp}.json", 
            mime="application/json",
            use_container_width=True
        )


def create_loading_spinner(message: str = "Loading...") -> None:
    """Create a custom loading spinner."""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="
            border: 4px solid #f3f4f6;
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem auto;
        "></div>
        <p style="color: var(--text-secondary); font-weight: 500;">{message}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)


def create_empty_state(title: str, message: str, action_label: str = None, icon: str = "📭") -> str:
    """Create an empty state with optional action."""
    action_html = ""
    if action_label:
        action_html = f'<button style="margin-top: 1rem; background: var(--primary-color); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; cursor: pointer;">{action_label}</button>'
    
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 1rem; color: var(--text-secondary);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">{title}</h3>
        <p style="margin-bottom: 1rem;">{message}</p>
        {action_html}
    </div>
    """, unsafe_allow_html=True)
    
    return action_label if action_label else None 