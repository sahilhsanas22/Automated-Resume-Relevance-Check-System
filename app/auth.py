"""
Simple authentication system for admin access
"""
import os
import hashlib
import streamlit as st
from typing import Optional

def get_admin_credentials() -> tuple[str, str]:
    """Get admin credentials from environment variables"""
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    return username, password

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username: str, password: str) -> bool:
    """Verify admin credentials"""
    admin_username, admin_password = get_admin_credentials()
    return username == admin_username and password == admin_password

def is_authenticated() -> bool:
    """Check if user is authenticated in current session"""
    return st.session_state.get("authenticated", False)

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user and set session state"""
    if verify_credentials(username, password):
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

def logout():
    """Logout user and clear session"""
    st.session_state.authenticated = False
    if "username" in st.session_state:
        del st.session_state.username

def require_auth():
    """Decorator-like function to require authentication"""
    if not is_authenticated():
        return False
    return True

def show_login_form() -> bool:
    """Show professional login form and handle authentication"""
    st.markdown("### Administrator Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if username and password:
                if authenticate_user(username, password):
                    st.success("Login successful!")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid credentials")
                    return False
            else:
                st.warning("Please enter both username and password")
                return False
    
    return False

def show_logout_button():
    """Show logout button for authenticated users"""
    if st.button("Logout", key="logout_btn", type="secondary"):
        logout()
        st.rerun()