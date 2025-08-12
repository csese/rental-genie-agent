#!/usr/bin/env python3
"""
Launcher script for the Rental Genie Dashboard
Handles environment setup and launches the Streamlit application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'requests',
        'pandas',
        'plotly',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("💡 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def setup_environment():
    """Setup environment variables and configuration"""
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Creating default .env file...")
        with open(env_file, 'w') as f:
            f.write("""# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Dashboard Configuration
DEBUG_MODE=False
ENABLE_MOCK_DATA=False

# Optional: Enable mock data for testing
# ENABLE_MOCK_DATA=True
""")
        print("✅ Created .env file with default settings")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"🔗 API Base URL: {os.getenv('API_BASE_URL', 'http://localhost:8000')}")
    print(f"🧪 Mock Data: {os.getenv('ENABLE_MOCK_DATA', 'False')}")

def test_api_connection():
    """Test connection to the Rental Genie API"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    api_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"⚠️ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Could not connect to API - using mock data mode")
        return False
    except Exception as e:
        print(f"⚠️ API connection error: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Rental Genie Dashboard...")
    print("📱 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main launcher function"""
    print("🏠 Rental Genie Dashboard Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ main.py not found. Please run this script from the dashboard directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Test API connection
    api_connected = test_api_connection()
    
    if not api_connected:
        print("\n💡 To use real data, make sure the Rental Genie API is running:")
        print("   python -m app.main")
        print("\n💡 Or enable mock data by setting ENABLE_MOCK_DATA=True in .env")
    
    print("\n" + "=" * 40)
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
