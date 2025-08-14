#!/usr/bin/env python3
"""
Test Runner Script for Robotics Dashboard Test Automation
This script provides an easy way to run different types of tests
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ Command completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "selenium", "pytest", "flask", "requests", "webdriver-manager"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Flask application...")
    
    # Check if app is already running
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Application is already running")
            return True
    except:
        pass
    
    # Start the application
    try:
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        time.sleep(5)
        
        # Check if it's running
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ Application started successfully")
                return True
            else:
                print("❌ Application failed to start properly")
                return False
        except Exception as e:
            print(f"❌ Application not accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def run_tests(test_type, browser="chrome", headless=False, parallel=False):
    """Run tests based on type"""
    print(f"\n🧪 Running {test_type} tests...")
    
    # Create test directories
    os.makedirs("test_reports", exist_ok=True)
    os.makedirs("test_screenshots", exist_ok=True)
    os.makedirs("test_logs", exist_ok=True)
    
    # Set environment variables
    env = os.environ.copy()
    env["BROWSER"] = browser
    env["HEADLESS"] = str(headless).lower()
    
    # Build pytest command
    cmd = [
        "python", "-m", "pytest",
        "-v",
        "--tb=short",
        "--html=test_reports/report.html",
        "--self-contained-html",
        "--cov=app",
        "--cov-report=html:test_reports/coverage",
        "--cov-report=term-missing",
        "--junitxml=test_reports/junit.xml",
        "--alluredir=test_reports/allure-results"
    ]
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    if test_type == "ui":
        cmd.extend(["tests/test_ui_dashboard.py", "-m", "ui"])
    elif test_type == "api":
        cmd.extend(["tests/test_api_endpoints.py", "-m", "api"])
    elif test_type == "integration":
        cmd.extend(["tests/test_integration.py", "-m", "integration"])
    elif test_type == "all":
        cmd.extend(["tests/"])
    else:
        print(f"❌ Unknown test type: {test_type}")
        return False
    
    # Run tests
    try:
        result = subprocess.run(cmd, env=env, check=True)
        print("✅ Tests completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False

def generate_reports():
    """Generate comprehensive test reports"""
    print("\n📊 Generating reports...")
    
    # Generate Allure report
    if run_command(["allure", "generate", "test_reports/allure-results", "--clean", "-o", "test_reports/allure-report"], 
                   "Generating Allure report"):
        print("✅ Allure report generated")
    
    # Generate coverage report
    if run_command(["python", "-m", "coverage", "report"], "Generating coverage report"):
        print("✅ Coverage report generated")
    
    print("\n📁 Reports generated in test_reports/ directory:")
    print("  - HTML Report: test_reports/report.html")
    print("  - Coverage Report: test_reports/coverage/index.html")
    print("  - Allure Report: test_reports/allure-report/index.html")
    print("  - JUnit XML: test_reports/junit.xml")

def main():
    parser = argparse.ArgumentParser(description="Robotics Dashboard Test Runner")
    parser.add_argument("--type", choices=["ui", "api", "integration", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--browser", choices=["chrome", "firefox"], 
                       default="chrome", help="Browser to use for UI tests")
    parser.add_argument("--headless", action="store_true", 
                       help="Run browser in headless mode")
    parser.add_argument("--parallel", action="store_true", 
                       help="Run tests in parallel")
    parser.add_argument("--no-start-app", action="store_true", 
                       help="Don't start the Flask application")
    parser.add_argument("--reports-only", action="store_true", 
                       help="Only generate reports from existing test results")
    
    args = parser.parse_args()
    
    print("🤖 Robotics Dashboard Test Automation")
    print("=" * 50)
    
    if args.reports_only:
        generate_reports()
        return
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start application if needed
    if not args.no_start_app:
        if not start_application():
            print("❌ Failed to start application. Exiting.")
            sys.exit(1)
    
    # Run tests
    if not run_tests(args.type, args.browser, args.headless, args.parallel):
        print("❌ Tests failed. Exiting.")
        sys.exit(1)
    
    # Generate reports
    generate_reports()
    
    print("\n🎉 Test execution completed successfully!")
    print("Check the test_reports/ directory for detailed results.")

if __name__ == "__main__":
    main() 