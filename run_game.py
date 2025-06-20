#!/usr/bin/env python3
"""
Launcher script for the Seymour Vertex Graph Game
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'networkx', 'plotly', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {missing_packages}")
        print("Installing missing packages...")
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Launch the Streamlit app."""
    print("🎯 Starting Seymour Vertex Graph Game...")
    
    # Check and install requirements
    check_requirements()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "seymour_graph_game.py")
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Game closed. Thanks for playing!")
    except Exception as e:
        print(f"Error launching app: {e}")
        print("Try running manually: streamlit run seymour_graph_game.py")

if __name__ == "__main__":
    main() 