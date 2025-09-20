"""
Startup script for the AI Resume Evaluation Engine
Runs both Streamlit frontend and FastAPI backend
"""
import subprocess
import sys
import time
import os

def install_spacy_model():
    """Install spaCy English model if not available"""
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("✅ spaCy model already installed")
    except OSError:
        print("📦 Installing spaCy English model...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print("✅ spaCy model installed successfully")

def start_fastapi():
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])

def start_streamlit():
    """Start Streamlit frontend"""
    print("🎨 Starting Streamlit frontend on http://localhost:8501")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "app/web/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

def main():
    print("🎯 AI Resume Evaluation Engine - Startup")
    print("=" * 50)
    
    # Install dependencies
    print("📦 Checking dependencies...")
    try:
        install_spacy_model()
    except Exception as e:
        print(f"⚠️ Warning: Could not install spaCy model: {e}")
    
    # Start services
    processes = []
    
    try:
        # Start FastAPI backend
        fastapi_process = start_fastapi()
        processes.append(fastapi_process)
        time.sleep(3)  # Wait for FastAPI to start
        
        # Start Streamlit frontend
        streamlit_process = start_streamlit()
        processes.append(streamlit_process)
        
        print("\n🎉 All services started successfully!")
        print("📱 Streamlit UI: http://localhost:8501")
        print("🔌 FastAPI Docs: http://localhost:8000/docs")
        print("📊 API Health: http://localhost:8000/health")
        print("\n🛑 Press Ctrl+C to stop all services")
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                for proc in processes:
                    if proc.poll() is not None:
                        print(f"⚠️ Process {proc.pid} terminated unexpectedly")
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
    
    except Exception as e:
        print(f"❌ Error starting services: {e}")
    
    finally:
        # Cleanup processes
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()