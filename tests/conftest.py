import pytest
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE_URL = "http://localhost:5000/api"
BROWSER = os.getenv("BROWSER", "chrome")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

@pytest.fixture(scope="session")
def setup_database():
    """Setup test database and sample data"""
    # This will be handled by the Flask app initialization
    pass

@pytest.fixture(scope="session")
def start_application():
    """Start the Flask application for testing"""
    import subprocess
    import time
    
    # Start the Flask app
    process = subprocess.Popen(
        ["python", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(5)
    
    # Check if app is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Application started successfully")
        else:
            print("❌ Application failed to start properly")
    except Exception as e:
        print(f"❌ Application not accessible: {e}")
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait()

@pytest.fixture(scope="function")
def driver():
    """Setup and teardown WebDriver for each test"""
    if BROWSER.lower() == "chrome":
        chrome_options = Options()
        if HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        raise ValueError(f"Unsupported browser: {BROWSER}")
    
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    # Take screenshot on test failure
    if hasattr(pytest, '_test_failed') and pytest._test_failed:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"test_screenshots/failure_{timestamp}.png"
        os.makedirs("test_screenshots", exist_ok=True)
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
    
    driver.quit()

@pytest.fixture(scope="function")
def wait(driver):
    """WebDriverWait instance for explicit waits"""
    return WebDriverWait(driver, 20)

@pytest.fixture(scope="function")
def api_client():
    """API client for testing REST endpoints"""
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.session = requests.Session()
        
        def get(self, endpoint, params=None):
            return self.session.get(f"{self.base_url}{endpoint}", params=params)
        
        def post(self, endpoint, data=None, json=None):
            return self.session.post(f"{self.base_url}{endpoint}", data=data, json=json)
        
        def put(self, endpoint, data=None, json=None):
            return self.session.put(f"{self.base_url}{endpoint}", data=data, json=json)
        
        def delete(self, endpoint):
            return self.session.delete(f"{self.base_url}{endpoint}")
    
    return APIClient(API_BASE_URL)

@pytest.fixture(scope="function")
def test_data():
    """Test data for various test scenarios"""
    return {
        "robot": {
            "name": "TestBot-001",
            "status": "idle",
            "battery_level": 95,
            "location": "Test Lab"
        },
        "invalid_robot": {
            "name": "",
            "status": "invalid_status",
            "battery_level": 150,
            "location": ""
        },
        "update_robot": {
            "status": "active",
            "battery_level": 80,
            "location": "Updated Location"
        }
    }

# Hook for test failure detection
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        pytest._test_failed = True
    else:
        pytest._test_failed = False 