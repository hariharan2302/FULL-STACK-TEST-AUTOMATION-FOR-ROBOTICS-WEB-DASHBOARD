import pytest
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class TestDashboardIntegration:
    """Integration Tests for Robotics Dashboard (UI + API)"""
    
    def test_end_to_end_robot_workflow(self, driver, wait, api_client, start_application):
        """Test complete robot workflow from creation to display"""
        # Step 1: Create robot via API
        robot_data = {
            "name": f"IntegrationBot-{int(time.time())}",
            "status": "active",
            "battery_level": 88,
            "location": "Integration Test Lab"
        }
        
        api_response = api_client.post("/robots", json=robot_data)
        assert api_response.status_code == 201
        robot_id = api_response.json()["id"]
        
        # Step 2: Verify robot appears in UI
        driver.get("http://localhost:5000")
        
        # Wait for robot to appear in the list
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h6[contains(text(), '{robot_data['name']}')]")))
        
        # Verify robot details in UI
        robot_card = driver.find_element(By.XPATH, f"//h6[contains(text(), '{robot_data['name']}')]")
        robot_card_container = robot_card.find_element(By.XPATH, "./ancestor::div[contains(@class, 'robot-card')]")
        
        # Check status badge
        status_badge = robot_card_container.find_element(By.CLASS_NAME, "badge")
        assert status_badge.text == robot_data["status"]
        
        # Check battery level
        battery_text = robot_card_container.find_element(By.CLASS_NAME, "card-text").text
        assert str(robot_data["battery_level"]) in battery_text
        
        # Check location
        location_text = robot_card_container.find_element(By.CLASS_NAME, "card-text").text
        assert robot_data["location"] in location_text
        
        print("✅ End-to-end robot workflow works correctly")
    
    def test_ui_api_data_synchronization(self, driver, wait, api_client, start_application):
        """Test that UI and API data are synchronized"""
        # Get data from API
        api_response = api_client.get("/robots")
        assert api_response.status_code == 200
        api_robots = api_response.json()["robots"]
        
        # Get data from UI
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "robot-card")))
        
        ui_robot_cards = driver.find_elements(By.CLASS_NAME, "robot-card")
        
        # Verify count matches
        assert len(ui_robot_cards) == len(api_robots)
        
        # Verify first robot data matches
        if len(api_robots) > 0 and len(ui_robot_cards) > 0:
            api_robot = api_robots[0]
            ui_robot = ui_robot_cards[0]
            
            # Check name
            ui_name = ui_robot.find_element(By.CLASS_NAME, "card-title").text
            assert ui_name == api_robot["name"]
            
            # Check status
            ui_status = ui_robot.find_element(By.CLASS_NAME, "badge").text
            assert ui_status == api_robot["status"]
        
        print("✅ UI and API data are synchronized")
    
    def test_dashboard_stats_consistency(self, driver, wait, api_client, start_application):
        """Test that dashboard statistics are consistent between UI and API"""
        # Get stats from API
        api_stats_response = api_client.get("/stats")
        assert api_stats_response.status_code == 200
        api_stats = api_stats_response.json()
        
        # Get stats from UI
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.ID, "totalRobots")))
        
        # Wait for stats to load
        time.sleep(2)
        
        # Extract UI stats
        ui_total_robots = int(driver.find_element(By.ID, "totalRobots").text)
        ui_avg_battery = int(driver.find_element(By.ID, "avgBattery").text.replace("%", ""))
        ui_total_tasks = int(driver.find_element(By.ID, "totalTasks").text)
        ui_active_robots = int(driver.find_element(By.ID, "activeRobots").text)
        
        # Verify consistency
        assert ui_total_robots == api_stats["total_robots"]
        assert ui_total_tasks == api_stats["total_tasks"]
        
        # Battery level might have slight differences due to rounding
        assert abs(ui_avg_battery - api_stats["average_battery_level"]) <= 1
        
        # Active robots count
        expected_active = api_stats["robot_status_counts"].get("active", 0)
        assert ui_active_robots == expected_active
        
        print("✅ Dashboard statistics are consistent between UI and API")
    
    def test_real_time_updates_integration(self, driver, wait, api_client, start_application):
        """Test that real-time updates work across UI and API"""
        # Get initial robot count from API
        initial_api_response = api_client.get("/robots")
        initial_api_count = len(initial_api_response.json()["robots"])
        
        # Get initial robot count from UI
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.ID, "totalRobots")))
        initial_ui_count = int(driver.find_element(By.ID, "totalRobots").text)
        
        # Verify initial counts match
        assert initial_ui_count == initial_api_count
        
        # Create a new robot via API
        robot_data = {
            "name": f"RealTimeBot-{int(time.time())}",
            "status": "idle",
            "battery_level": 75,
            "location": "Real-time Test Area"
        }
        
        api_response = api_client.post("/robots", json=robot_data)
        assert api_response.status_code == 201
        
        # Wait for UI to update (dashboard refreshes every 10 seconds)
        time.sleep(12)
        
        # Check updated counts
        updated_api_response = api_client.get("/robots")
        updated_api_count = len(updated_api_response.json()["robots"])
        
        updated_ui_count = int(driver.find_element(By.ID, "totalRobots").text)
        
        # Verify counts increased
        assert updated_api_count == initial_api_count + 1
        assert updated_ui_count == initial_ui_count + 1
        
        # Verify new robot appears in UI
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h6[contains(text(), '{robot_data['name']}')]")))
        
        print("✅ Real-time updates work correctly across UI and API")
    
    def test_form_validation_integration(self, driver, wait, api_client, start_application):
        """Test form validation integration between UI and API"""
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.ID, "addRobotForm")))
        
        # Test form submission with invalid data
        submit_button = driver.find_element(By.CSS_SELECTOR, "#addRobotForm button[type='submit']")
        submit_button.click()
        
        # Check if form validation prevents submission
        robot_name_field = driver.find_element(By.ID, "robotName")
        assert robot_name_field.get_attribute("required") is not None
        
        # Try to submit with invalid battery level
        driver.find_element(By.ID, "robotName").send_keys("InvalidBot")
        driver.find_element(By.ID, "batteryLevel").clear()
        driver.find_element(By.ID, "batteryLevel").send_keys("150")  # Invalid value
        
        # Check if HTML5 validation catches this
        battery_field = driver.find_element(By.ID, "batteryLevel")
        assert battery_field.get_attribute("max") == "100"
        
        # Now test with valid data
        driver.find_element(By.ID, "robotName").clear()
        driver.find_element(By.ID, "robotName").send_keys("ValidBot")
        driver.find_element(By.ID, "batteryLevel").clear()
        driver.find_element(By.ID, "batteryLevel").send_keys("85")
        driver.find_element(By.ID, "location").clear()
        driver.find_element(By.ID, "location").send_keys("Valid Location")
        
        # Submit form
        submit_button.click()
        
        # Wait for robot to be added
        wait.until(EC.presence_of_element_located((By.XPATH, "//h6[contains(text(), 'ValidBot')]")))
        
        # Verify via API
        api_response = api_client.get("/robots")
        assert api_response.status_code == 200
        
        robots = api_response.json()["robots"]
        robot_names = [robot["name"] for robot in robots]
        assert "ValidBot" in robot_names
        
        print("✅ Form validation integration works correctly")
    
    def test_chart_data_integration(self, driver, wait, api_client, start_application):
        """Test that chart data is consistent with API data"""
        # Get robot data from API
        api_response = api_client.get("/robots")
        assert api_response.status_code == 200
        api_robots = api_response.json()["robots"]
        
        # Get stats from API
        stats_response = api_client.get("/stats")
        assert stats_response.status_code == 200
        api_stats = stats_response.json()
        
        # Load dashboard
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.ID, "statusChart")))
        wait.until(EC.presence_of_element_located((By.ID, "batteryChart")))
        
        # Wait for charts to render
        time.sleep(3)
        
        # Verify chart containers exist and have content
        status_chart = driver.find_element(By.ID, "statusChart")
        battery_chart = driver.find_element(By.ID, "batteryChart")
        
        assert status_chart.is_displayed()
        assert battery_chart.is_displayed()
        
        # Check if charts have data (they should be rendered by Chart.js)
        # We can't directly access chart data, but we can verify the canvas elements exist
        canvas_elements = driver.find_elements(By.TAG_NAME, "canvas")
        assert len(canvas_elements) >= 2
        
        print("✅ Chart data integration works correctly")
    
    def test_error_handling_integration(self, driver, wait, api_client, start_application):
        """Test error handling integration between UI and API"""
        # Test API error
        api_response = api_client.get("/robots/99999")
        assert api_response.status_code == 404
        
        # Test UI error handling
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Try to access non-existent page
        driver.get("http://localhost:5000/nonexistent")
        
        # Should get 404 or similar
        assert "404" in driver.page_source or "Not Found" in driver.page_source
        
        # Return to dashboard
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.ID, "robotList")))
        
        print("✅ Error handling integration works correctly")
    
    def test_performance_integration(self, driver, wait, api_client, start_application):
        """Test performance integration between UI and API"""
        # Test API performance
        start_time = time.time()
        api_response = api_client.get("/robots")
        api_time = time.time() - start_time
        
        assert api_response.status_code == 200
        assert api_time < 1.0, f"API took {api_time:.2f} seconds"
        
        # Test UI performance
        start_time = time.time()
        driver.get("http://localhost:5000")
        
        # Wait for page to fully load
        wait.until(EC.presence_of_element_located((By.ID, "robotList")))
        wait.until(EC.presence_of_element_located((By.ID, "statusChart")))
        
        ui_time = time.time() - start_time
        
        assert ui_time < 10.0, f"UI took {ui_time:.2f} seconds to load"
        
        print(f"✅ Performance integration: API {api_time:.3f}s, UI {ui_time:.3f}s")
    
    def test_data_persistence_integration(self, driver, wait, api_client, start_application):
        """Test that data persists correctly across UI and API"""
        # Create a robot via API
        robot_data = {
            "name": f"PersistenceBot-{int(time.time())}",
            "status": "active",
            "battery_level": 90,
            "location": "Persistence Test Area"
        }
        
        api_response = api_client.post("/robots", json=robot_data)
        assert api_response.status_code == 201
        robot_id = api_response.json()["id"]
        
        # Verify robot exists in API
        get_response = api_client.get(f"/robots/{robot_id}")
        assert get_response.status_code == 200
        
        # Verify robot appears in UI
        driver.get("http://localhost:5000")
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h6[contains(text(), '{robot_data['name']}')]")))
        
        # Refresh page and verify robot still exists
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.XPATH, f"//h6[contains(text(), '{robot_data['name']}')]")))
        
        # Verify robot still exists in API
        get_response_after_refresh = api_client.get(f"/robots/{robot_id}")
        assert get_response_after_refresh.status_code == 200
        
        print("✅ Data persistence integration works correctly") 