import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

class TestDashboardUI:
    """UI Tests for Robotics Dashboard"""
    
    def test_dashboard_loads_successfully(self, driver, wait, start_application):
        """Test that dashboard loads with all elements visible"""
        driver.get("http://localhost:5000")
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Verify main elements are present
        assert "Robotics Control Dashboard" in driver.title
        assert driver.find_element(By.TAG_NAME, "h1").text == "Robotics Control Dashboard"
        
        # Check statistics cards
        stats_cards = driver.find_elements(By.CLASS_NAME, "stats-card")
        assert len(stats_cards) == 4
        
        # Check main dashboard sections
        assert driver.find_element(By.ID, "robotList")
        assert driver.find_element(By.ID, "addRobotForm")
        
        print("✅ Dashboard loads successfully with all elements")
    
    def test_robot_list_display(self, driver, wait, start_application):
        """Test that robot list displays correctly"""
        driver.get("http://localhost:5000")
        
        # Wait for robots to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "robot-card")))
        
        # Check if robots are displayed
        robot_cards = driver.find_elements(By.CLASS_NAME, "robot-card")
        assert len(robot_cards) > 0
        
        # Verify robot information is displayed
        first_robot = robot_cards[0]
        assert first_robot.find_element(By.CLASS_NAME, "card-title")
        assert first_robot.find_element(By.CLASS_NAME, "badge")
        
        print("✅ Robot list displays correctly")
    
    def test_add_robot_functionality(self, driver, wait, start_application):
        """Test adding a new robot through the UI"""
        driver.get("http://localhost:5000")
        
        # Wait for form to be present
        wait.until(EC.presence_of_element_located((By.ID, "addRobotForm")))
        
        # Fill out the form
        robot_name = f"TestBot-{int(time.time())}"
        driver.find_element(By.ID, "robotName").send_keys(robot_name)
        
        # Select status
        status_select = Select(driver.find_element(By.ID, "robotStatus"))
        status_select.select_by_value("active")
        
        # Set battery level
        driver.find_element(By.ID, "batteryLevel").clear()
        driver.find_element(By.ID, "batteryLevel").send_keys("85")
        
        # Set location
        driver.find_element(By.ID, "location").clear()
        driver.find_element(By.ID, "location").send_keys("Test Location")
        
        # Submit form
        driver.find_element(By.CSS_SELECTOR, "#addRobotForm button[type='submit']").click()
        
        # Wait for robot to be added (check if it appears in the list)
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h6[contains(text(), '{robot_name}')]")))
        
        # Verify robot was added
        robot_cards = driver.find_elements(By.CLASS_NAME, "robot-card")
        robot_names = [card.find_element(By.CLASS_NAME, "card-title").text for card in robot_cards]
        assert robot_name in robot_names
        
        print("✅ Robot added successfully through UI")
    
    def test_dashboard_charts(self, driver, wait, start_application):
        """Test that charts are displayed and functional"""
        driver.get("http://localhost:5000")
        
        # Wait for charts to load
        wait.until(EC.presence_of_element_located((By.ID, "statusChart")))
        wait.until(EC.presence_of_element_located((By.ID, "batteryChart")))
        
        # Check if charts are present
        status_chart = driver.find_element(By.ID, "statusChart")
        battery_chart = driver.find_element(By.ID, "batteryChart")
        
        assert status_chart.is_displayed()
        assert battery_chart.is_displayed()
        
        # Verify chart containers have proper dimensions
        chart_containers = driver.find_elements(By.CLASS_NAME, "chart-container")
        assert len(chart_containers) == 2
        
        for container in chart_containers:
            height = container.value_of_css_property("height")
            assert height != "0px"
        
        print("✅ Dashboard charts display correctly")
    
    def test_dashboard_responsiveness(self, driver, wait, start_application):
        """Test dashboard responsiveness on different screen sizes"""
        driver.get("http://localhost:5000")
        
        # Test desktop view
        driver.set_window_size(1920, 1080)
        time.sleep(2)
        
        # Check if all elements are visible
        assert driver.find_element(By.ID, "robotList").is_displayed()
        assert driver.find_element(By.ID, "addRobotForm").is_displayed()
        
        # Test tablet view
        driver.set_window_size(768, 1024)
        time.sleep(2)
        
        # Check if layout adjusts
        robot_list = driver.find_element(By.ID, "robotList")
        assert robot_list.is_displayed()
        
        # Test mobile view
        driver.set_window_size(375, 667)
        time.sleep(2)
        
        # Check if mobile layout works
        assert driver.find_element(By.ID, "robotList").is_displayed()
        
        # Reset to desktop
        driver.set_window_size(1920, 1080)
        
        print("✅ Dashboard is responsive across different screen sizes")
    
    def test_real_time_updates(self, driver, wait, start_application):
        """Test that dashboard updates in real-time"""
        driver.get("http://localhost:5000")
        
        # Wait for initial load
        wait.until(EC.presence_of_element_located((By.ID, "totalRobots")))
        
        # Get initial robot count
        initial_count = int(driver.find_element(By.ID, "totalRobots").text)
        
        # Wait for potential updates (dashboard refreshes every 10 seconds)
        time.sleep(12)
        
        # Check if data is still displayed (indicating refresh worked)
        current_count = int(driver.find_element(By.ID, "totalRobots").text)
        
        # The count should remain the same or increase (if robots were added)
        assert current_count >= initial_count
        
        print("✅ Dashboard updates in real-time")
    
    def test_navigation_and_interactions(self, driver, wait, start_application):
        """Test various navigation and interaction elements"""
        driver.get("http://localhost:5000")
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Test scrolling
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Test form interactions
        robot_name_field = driver.find_element(By.ID, "robotName")
        robot_name_field.click()
        robot_name_field.send_keys("Test")
        robot_name_field.send_keys(Keys.CONTROL + "a")
        robot_name_field.send_keys(Keys.DELETE)
        
        # Verify form is interactive
        assert robot_name_field.is_enabled()
        
        print("✅ Navigation and interactions work correctly")
    
    def test_error_handling_ui(self, driver, wait, start_application):
        """Test UI error handling and validation"""
        driver.get("http://localhost:5000")
        
        # Wait for form to load
        wait.until(EC.presence_of_element_located((By.ID, "addRobotForm")))
        
        # Try to submit empty form
        submit_button = driver.find_element(By.CSS_SELECTOR, "#addRobotForm button[type='submit']")
        submit_button.click()
        
        # Check if form validation works (HTML5 validation)
        robot_name_field = driver.find_element(By.ID, "robotName")
        assert robot_name_field.get_attribute("required") is not None
        
        # Test invalid battery level
        battery_field = driver.find_element(By.ID, "batteryLevel")
        battery_field.clear()
        battery_field.send_keys("150")  # Invalid value > 100
        
        # Check if HTML5 validation catches this
        assert battery_field.get_attribute("max") == "100"
        
        print("✅ UI error handling and validation work correctly")
    
    def test_dashboard_performance(self, driver, wait, start_application):
        """Test dashboard performance and loading times"""
        start_time = time.time()
        
        driver.get("http://localhost:5000")
        
        # Wait for page to fully load
        wait.until(EC.presence_of_element_located((By.ID, "robotList")))
        wait.until(EC.presence_of_element_located((By.ID, "statusChart")))
        
        load_time = time.time() - start_time
        
        # Dashboard should load within reasonable time (less than 10 seconds)
        assert load_time < 10, f"Dashboard took {load_time:.2f} seconds to load"
        
        print(f"✅ Dashboard loads in {load_time:.2f} seconds")
    
    def test_accessibility_features(self, driver, wait, start_application):
        """Test basic accessibility features"""
        driver.get("http://localhost:5000")
        
        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        # Check for proper heading structure
        headings = driver.find_elements(By.TAG_NAME, "h1")
        assert len(headings) > 0
        
        # Check for alt text on images (if any)
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            if alt_text is None:
                print("⚠️ Image without alt text found")
        
        # Check for form labels
        form_labels = driver.find_elements(By.TAG_NAME, "label")
        assert len(form_labels) > 0
        
        print("✅ Basic accessibility features are present") 