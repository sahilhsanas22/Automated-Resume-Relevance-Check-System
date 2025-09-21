"""
Main entry point for Streamlit Cloud deployment
This file should be in the root directory for Streamlit Cloud to detect it automatically
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the main application
from app.web.streamlit_app import main

if __name__ == "__main__":
    main()