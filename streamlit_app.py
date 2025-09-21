"""
Main entry point for Streamlit Cloud deployment
This file should be in the root directory for Streamlit Cloud to detect it automatically
"""

import sys
import os

# Add the project root to Python path - more robust for cloud deployment
try:
    # First try to use __file__ (works in most environments)
    project_root = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback to current working directory (for some cloud environments)
    project_root = os.getcwd()

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the main application
try:
    from app.web.streamlit_app import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    import streamlit as st
    st.error("🚨 **Application Failed to Start**")
    st.error(f"Import Error: {e}")
    
    with st.expander("🔧 Debug Information"):
        st.write("**Python Path:**")
        for i, path in enumerate(sys.path[:5]):
            st.write(f"{i}: {path}")
        
        st.write("**Working Directory:**", os.getcwd())
        st.write("**Project Root:**", project_root)
        
        # Check if app directory exists
        app_dir = os.path.join(project_root, "app")
        st.write(f"**App directory exists:** {os.path.exists(app_dir)}")
        
        if os.path.exists(app_dir):
            st.write("**App directory contents:**")
            try:
                contents = os.listdir(app_dir)
                for item in contents:
                    st.write(f"- {item}")
            except Exception as ex:
                st.write(f"Error listing contents: {ex}")
    
    st.info("💡 **Troubleshooting Tips:**")
    st.write("1. Ensure all files are properly uploaded to Streamlit Cloud")
    st.write("2. Check that requirements.txt includes all dependencies")
    st.write("3. Verify Python version compatibility (using Python 3.13)")
    st.write("4. Check the deployment logs for more detailed error messages")
    
    st.stop()
except Exception as e:
    import streamlit as st
    st.error("🚨 **Unexpected Application Error**")
    st.error(f"Error: {e}")
    import traceback
    with st.expander("🔍 Full Error Details"):
        st.code(traceback.format_exc())
    st.stop()