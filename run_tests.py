#!/usr/bin/env python3
"""
Test runner script for CI/CD compatibility
This script ensures tests run regardless of directory structure
"""

import os
import sys
import subprocess
from pathlib import Path

def find_tests_directory():
    """Find tests directory in various possible locations"""
    current_dir = Path.cwd()
    
    # Possible paths where tests might be
    possible_paths = [
        current_dir / "tests",
        current_dir / "Flight_Price_Predictor" / "tests",
        current_dir / "Flight_Price_Predictor" / "Flight_Price_Predictor" / "tests",
        current_dir.parent / "tests",
        Path("/home/runner/work/Flight_Price_Predictor/Flight_Price_Predictor") / "tests",
        Path("/home/runner/work/Flight_Price_Predictor") / "tests",
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            print(f"Found tests directory: {path}")
            return str(path)
    
    print("Tests directory not found in any expected location")
    return None

def run_pytest(tests_path):
    """Run pytest with proper path"""
    try:
        cmd = [
            sys.executable, "-m", "pytest",
            tests_path,
            "--cov=.",
            "--cov-report=xml",
            "--cov-report=html",
            "--tb=short",
            "-v"
        ]
        
        print(f"Running pytest with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Tests completed successfully!")
            print(result.stdout)
        else:
            print(f"❌ Tests failed with exit code {result.returncode}")
            print(result.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return 1

if __name__ == "__main__":
    print("🧪 Flight Price Predictor Test Runner")
    print("=" * 50)
    
    # Find tests directory
    tests_path = find_tests_directory()
    
    if tests_path:
        print(f"✅ Using tests directory: {tests_path}")
        exit_code = run_pytest(tests_path)
        sys.exit(exit_code)
    else:
        print("❌ Could not find tests directory!")
        print("📁 Current directory contents:")
        
        current_dir = Path.cwd()
        for item in current_dir.iterdir():
            print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")
        
        print("\n🔍 Attempting to run tests anyway...")
        # Try to run tests anyway
        exit_code = run_pytest("tests")
        sys.exit(exit_code)
