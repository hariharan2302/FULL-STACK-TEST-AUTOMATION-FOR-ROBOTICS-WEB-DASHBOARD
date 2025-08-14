import pytest
import json
import time
from datetime import datetime

class TestRoboticsAPI:
    """API Tests for Robotics Dashboard REST Endpoints"""
    
    def test_health_check_endpoint(self, api_client):
        """Test the health check endpoint"""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        
        print("✅ Health check endpoint works correctly")
    
    def test_get_robots_list(self, api_client):
        """Test getting the list of all robots"""
        response = api_client.get("/robots")
        
        assert response.status_code == 200
        data = response.json()
        assert "robots" in data
        assert isinstance(data["robots"], list)
        assert len(data["robots"]) > 0
        
        # Verify robot structure
        first_robot = data["robots"][0]
        required_fields = ["id", "name", "status", "battery_level", "location", "last_updated"]
        for field in required_fields:
            assert field in first_robot
        
        print("✅ Get robots list endpoint works correctly")
    
    def test_get_robot_by_id(self, api_client):
        """Test getting a specific robot by ID"""
        # First get the list to get a valid robot ID
        robots_response = api_client.get("/robots")
        assert robots_response.status_code == 200
        
        robots = robots_response.json()["robots"]
        assert len(robots) > 0
        
        robot_id = robots[0]["id"]
        
        # Get specific robot
        response = api_client.get(f"/robots/{robot_id}")
        
        assert response.status_code == 200
        robot = response.json()
        assert robot["id"] == robot_id
        assert robot["name"] == robots[0]["name"]
        
        print("✅ Get robot by ID endpoint works correctly")
    
    def test_get_nonexistent_robot(self, api_client):
        """Test getting a robot that doesn't exist"""
        response = api_client.get("/robots/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"] == "Robot not found"
        
        print("✅ Get nonexistent robot returns proper error")
    
    def test_create_new_robot(self, api_client, test_data):
        """Test creating a new robot"""
        robot_data = test_data["robot"]
        
        response = api_client.post("/robots", json=robot_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert data["message"] == "Robot created successfully"
        assert "id" in data
        assert isinstance(data["id"], int)
        
        # Verify robot was created by fetching it
        robot_id = data["id"]
        get_response = api_client.get(f"/robots/{robot_id}")
        assert get_response.status_code == 200
        
        created_robot = get_response.json()
        assert created_robot["name"] == robot_data["name"]
        assert created_robot["status"] == robot_data["status"]
        assert created_robot["battery_level"] == robot_data["battery_level"]
        assert created_robot["location"] == robot_data["location"]
        
        print("✅ Create robot endpoint works correctly")
    
    def test_create_robot_with_invalid_data(self, api_client, test_data):
        """Test creating a robot with invalid data"""
        invalid_data = test_data["invalid_robot"]
        
        response = api_client.post("/robots", json=invalid_data)
        
        # Should return 400 or similar error status
        assert response.status_code in [400, 422, 500]
        
        print("✅ Create robot with invalid data returns proper error")
    
    def test_update_robot(self, api_client, test_data):
        """Test updating an existing robot"""
        # First create a robot
        create_response = api_client.post("/robots", json=test_data["robot"])
        assert create_response.status_code == 201
        robot_id = create_response.json()["id"]
        
        # Update the robot
        update_data = test_data["update_robot"]
        response = api_client.put(f"/robots/{robot_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Robot updated successfully"
        
        # Verify the update
        get_response = api_client.get(f"/robots/{robot_id}")
        assert get_response.status_code == 200
        
        updated_robot = get_response.json()
        assert updated_robot["status"] == update_data["status"]
        assert updated_robot["battery_level"] == update_data["battery_level"]
        assert updated_robot["location"] == update_data["location"]
        
        print("✅ Update robot endpoint works correctly")
    
    def test_update_nonexistent_robot(self, api_client, test_data):
        """Test updating a robot that doesn't exist"""
        update_data = test_data["update_robot"]
        response = api_client.put("/robots/99999", json=update_data)
        
        # Should return 404 or similar error status
        assert response.status_code in [404, 500]
        
        print("✅ Update nonexistent robot returns proper error")
    
    def test_get_tasks_list(self, api_client):
        """Test getting the list of all tasks"""
        response = api_client.get("/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        
        # If there are tasks, verify their structure
        if len(data["tasks"]) > 0:
            first_task = data["tasks"][0]
            required_fields = ["id", "robot_id", "task_type", "status", "priority", "created_at"]
            for field in required_fields:
                assert field in first_task
        
        print("✅ Get tasks list endpoint works correctly")
    
    def test_get_sensor_data(self, api_client):
        """Test getting sensor data"""
        response = api_client.get("/sensor-data")
        
        assert response.status_code == 200
        data = response.json()
        assert "sensor_data" in data
        assert isinstance(data["sensor_data"], list)
        
        print("✅ Get sensor data endpoint works correctly")
    
    def test_get_sensor_data_by_robot(self, api_client):
        """Test getting sensor data filtered by robot ID"""
        # First get a robot ID
        robots_response = api_client.get("/robots")
        assert robots_response.status_code == 200
        
        robots = robots_response.json()["robots"]
        if len(robots) > 0:
            robot_id = robots[0]["id"]
            
            response = api_client.get(f"/sensor-data?robot_id={robot_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert "sensor_data" in data
            assert isinstance(data["sensor_data"], list)
            
            print("✅ Get sensor data by robot ID works correctly")
    
    def test_get_dashboard_stats(self, api_client):
        """Test getting dashboard statistics"""
        response = api_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        required_fields = [
            "robot_status_counts", "average_battery_level", 
            "task_status_counts", "total_robots", "total_tasks"
        ]
        for field in required_fields:
            assert field in data
        
        # Verify data types
        assert isinstance(data["robot_status_counts"], dict)
        assert isinstance(data["average_battery_level"], (int, float))
        assert isinstance(data["task_status_counts"], dict)
        assert isinstance(data["total_robots"], int)
        assert isinstance(data["total_tasks"], int)
        
        print("✅ Get dashboard stats endpoint works correctly")
    
    def test_api_response_headers(self, api_client):
        """Test that API responses have proper headers"""
        response = api_client.get("/robots")
        
        assert response.status_code == 200
        headers = response.headers
        
        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in headers
        assert "Content-Type" in headers
        assert "application/json" in headers["Content-Type"]
        
        print("✅ API responses have proper headers")
    
    def test_api_error_handling(self, api_client):
        """Test API error handling for various scenarios"""
        # Test invalid endpoint
        response = api_client.get("/invalid-endpoint")
        assert response.status_code == 404
        
        # Test invalid HTTP method
        response = api_client.post("/robots/1")  # POST to specific robot endpoint
        assert response.status_code in [405, 404, 500]  # Method not allowed or similar
        
        print("✅ API error handling works correctly")
    
    def test_api_performance(self, api_client):
        """Test API response times"""
        endpoints = ["/health", "/robots", "/tasks", "/stats"]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = api_client.get(endpoint)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 2.0, f"Endpoint {endpoint} took {response_time:.2f} seconds"
            
            print(f"✅ {endpoint} responded in {response_time:.3f} seconds")
    
    def test_api_data_consistency(self, api_client):
        """Test that API data is consistent across calls"""
        # Get robots list twice
        response1 = api_client.get("/robots")
        response2 = api_client.get("/robots")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Basic consistency check
        assert len(data1["robots"]) == len(data2["robots"])
        
        # If robots exist, check first robot is same
        if len(data1["robots"]) > 0:
            robot1 = data1["robots"][0]
            robot2 = data2["robots"][0]
            assert robot1["id"] == robot2["id"]
            assert robot1["name"] == robot2["name"]
        
        print("✅ API data is consistent across calls")
    
    def test_api_authentication_not_required(self, api_client):
        """Test that API endpoints don't require authentication"""
        # Test without any authentication headers
        response = api_client.get("/robots")
        assert response.status_code == 200
        
        # Test with invalid auth header
        headers = {"Authorization": "Bearer invalid-token"}
        response = api_client.get("/robots", headers=headers)
        assert response.status_code == 200
        
        print("✅ API endpoints don't require authentication")
    
    def test_api_rate_limiting(self, api_client):
        """Test API behavior under multiple rapid requests"""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = api_client.get("/health")
            responses.append(response.status_code)
            time.sleep(0.1)  # Small delay between requests
        
        # All requests should succeed
        assert all(status == 200 for status in responses)
        
        print("✅ API handles rapid requests correctly") 