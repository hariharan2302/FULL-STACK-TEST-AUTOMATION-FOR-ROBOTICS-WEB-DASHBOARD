from locust import HttpUser, task, between
import json
import random

class RoboticsDashboardUser(HttpUser):
    """Performance test user for Robotics Dashboard"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Setup user session"""
        self.client.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @task(3)
    def get_health_check(self):
        """Test health check endpoint - high frequency"""
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(5)
    def get_robots_list(self):
        """Test getting robots list - very high frequency"""
        with self.client.get("/api/robots", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "robots" in data and isinstance(data["robots"], list):
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(2)
    def get_dashboard_stats(self):
        """Test getting dashboard statistics - medium frequency"""
        with self.client.get("/api/stats", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_robots", "average_battery_level", "total_tasks"]
                if all(field in data for field in required_fields):
                    response.success()
                else:
                    response.failure("Missing required fields")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)
    def create_robot(self):
        """Test creating a robot - low frequency"""
        robot_data = {
            "name": f"PerfBot-{random.randint(1000, 9999)}",
            "status": random.choice(["idle", "active", "maintenance"]),
            "battery_level": random.randint(20, 100),
            "location": random.choice(["Lab A", "Warehouse B", "Production Line"])
        }
        
        with self.client.post("/api/robots", 
                             json=robot_data, 
                             catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                if "id" in data and "message" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Expected 201, got {response.status_code}")
    
    @task(1)
    def get_robot_by_id(self):
        """Test getting robot by ID - low frequency"""
        # First get a robot ID from the list
        robots_response = self.client.get("/api/robots")
        if robots_response.status_code == 200:
            robots = robots_response.json().get("robots", [])
            if robots:
                robot_id = random.choice(robots)["id"]
                
                with self.client.get(f"/api/robots/{robot_id}", 
                                   catch_response=True) as response:
                    if response.status_code == 200:
                        data = response.json()
                        if "id" in data and "name" in data:
                            response.success()
                        else:
                            response.failure("Invalid robot data")
                    else:
                        response.failure(f"Expected 200, got {response.status_code}")
            else:
                # No robots available, skip this test
                pass
    
    @task(1)
    def update_robot(self):
        """Test updating a robot - low frequency"""
        # First get a robot ID from the list
        robots_response = self.client.get("/api/robots")
        if robots_response.status_code == 200:
            robots = robots_response.json().get("robots", [])
            if robots:
                robot_id = random.choice(robots)["id"]
                
                update_data = {
                    "status": random.choice(["idle", "active", "maintenance"]),
                    "battery_level": random.randint(20, 100),
                    "location": random.choice(["Updated Lab", "New Warehouse", "Maintenance Bay"])
                }
                
                with self.client.put(f"/api/robots/{robot_id}", 
                                   json=update_data, 
                                   catch_response=True) as response:
                    if response.status_code == 200:
                        data = response.json()
                        if "message" in data:
                            response.success()
                        else:
                            response.failure("Invalid response format")
                    else:
                        response.failure(f"Expected 200, got {response.status_code}")
    
    @task(2)
    def get_tasks_list(self):
        """Test getting tasks list - medium frequency"""
        with self.client.get("/api/tasks", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "tasks" in data and isinstance(data["tasks"], list):
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)
    def get_sensor_data(self):
        """Test getting sensor data - low frequency"""
        with self.client.get("/api/sensor-data", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "sensor_data" in data and isinstance(data["sensor_data"], list):
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)
    def get_sensor_data_by_robot(self):
        """Test getting sensor data filtered by robot - low frequency"""
        # First get a robot ID from the list
        robots_response = self.client.get("/api/robots")
        if robots_response.status_code == 200:
            robots = robots_response.json().get("robots", [])
            if robots:
                robot_id = random.choice(robots)["id"]
                
                with self.client.get(f"/api/sensor-data?robot_id={robot_id}", 
                                   catch_response=True) as response:
                    if response.status_code == 200:
                        data = response.json()
                        if "sensor_data" in data:
                            response.success()
                        else:
                            response.failure("Invalid response format")
                    else:
                        response.failure(f"Expected 200, got {response.status_code}")
    
    @task(1)
    def test_dashboard_page(self):
        """Test loading the main dashboard page - low frequency"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                if "Robotics Control Dashboard" in response.text:
                    response.success()
                else:
                    response.failure("Dashboard content not found")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

class HighLoadUser(RoboticsDashboardUser):
    """High load user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task(10)
    def rapid_health_checks(self):
        """Rapid health check requests for stress testing"""
        self.get_health_check()
    
    @task(8)
    def rapid_robots_list(self):
        """Rapid robots list requests for stress testing"""
        self.get_robots_list()

class APIOnlyUser(HttpUser):
    """API-only user for backend performance testing"""
    
    wait_time = between(0.5, 1.5)
    
    def on_start(self):
        """Setup user session"""
        self.client.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @task(5)
    def api_health_check(self):
        """API health check"""
        self.client.get("/api/health")
    
    @task(3)
    def api_robots_list(self):
        """API robots list"""
        self.client.get("/api/robots")
    
    @task(2)
    def api_stats(self):
        """API statistics"""
        self.client.get("/api/stats")
    
    @task(1)
    def api_create_robot(self):
        """API create robot"""
        robot_data = {
            "name": f"APIBot-{random.randint(1000, 9999)}",
            "status": "idle",
            "battery_level": 100,
            "location": "API Test Lab"
        }
        self.client.post("/api/robots", json=robot_data) 