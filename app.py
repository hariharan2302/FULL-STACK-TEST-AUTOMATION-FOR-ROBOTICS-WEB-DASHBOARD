from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_restful import Api, Resource
import sqlite3
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)
api = Api(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('robotics_dashboard.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS robots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            battery_level INTEGER,
            location TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id INTEGER,
            task_type TEXT NOT NULL,
            status TEXT NOT NULL,
            priority INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (robot_id) REFERENCES robots (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            robot_id INTEGER,
            sensor_type TEXT NOT NULL,
            value REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (robot_id) REFERENCES robots (id)
        )
    ''')
    
    # Insert sample data
    sample_robots = [
        ('R2D2', 'active', 85, 'Warehouse A'),
        ('C3PO', 'idle', 92, 'Lab B'),
        ('BB8', 'active', 67, 'Production Line'),
        ('WALL-E', 'maintenance', 45, 'Service Bay'),
        ('Optimus', 'active', 78, 'Assembly Line')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO robots (name, status, battery_level, location)
        VALUES (?, ?, ?, ?)
    ''', sample_robots)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# API Resources
class RobotList(Resource):
    def get(self):
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM robots')
        robots = cursor.fetchall()
        conn.close()
        
        robot_list = []
        for robot in robots:
            robot_list.append({
                'id': robot[0],
                'name': robot[1],
                'status': robot[2],
                'battery_level': robot[3],
                'location': robot[4],
                'last_updated': robot[5]
            })
        
        return {'robots': robot_list}
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        status = data.get('status', 'idle')
        battery_level = data.get('battery_level', 100)
        location = data.get('location', 'Unknown')
        
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO robots (name, status, battery_level, location)
            VALUES (?, ?, ?, ?)
        ''', (name, status, battery_level, location))
        robot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'message': 'Robot created successfully', 'id': robot_id}, 201

class RobotDetail(Resource):
    def get(self, robot_id):
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM robots WHERE id = ?', (robot_id,))
        robot = cursor.fetchone()
        conn.close()
        
        if robot:
            return {
                'id': robot[0],
                'name': robot[1],
                'status': robot[2],
                'battery_level': robot[3],
                'location': robot[4],
                'last_updated': robot[5]
            }
        return {'error': 'Robot not found'}, 404
    
    def put(self, robot_id):
        data = request.get_json()
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE robots 
            SET status = ?, battery_level = ?, location = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (data.get('status'), data.get('battery_level'), data.get('location'), robot_id))
        
        conn.commit()
        conn.close()
        
        return {'message': 'Robot updated successfully'}

class TaskList(Resource):
    def get(self):
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()
        conn.close()
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task[0],
                'robot_id': task[1],
                'task_type': task[2],
                'status': task[3],
                'priority': task[4],
                'created_at': task[5]
            })
        
        return {'tasks': task_list}

class SensorData(Resource):
    def get(self):
        robot_id = request.args.get('robot_id')
        conn = sqlite3.connect('robotics_dashboard.db')
        cursor = conn.cursor()
        
        if robot_id:
            cursor.execute('SELECT * FROM sensor_data WHERE robot_id = ? ORDER BY timestamp DESC LIMIT 100', (robot_id,))
        else:
            cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100')
        
        data = cursor.fetchall()
        conn.close()
        
        sensor_list = []
        for sensor in data:
            sensor_list.append({
                'id': sensor[0],
                'robot_id': sensor[1],
                'sensor_type': sensor[2],
                'value': sensor[3],
                'timestamp': sensor[4]
            })
        
        return {'sensor_data': sensor_list}

# Add API resources
api.add_resource(RobotList, '/api/robots')
api.add_resource(RobotDetail, '/api/robots/<int:robot_id>')
api.add_resource(TaskList, '/api/tasks')
api.add_resource(SensorData, '/api/sensor-data')

# Dashboard routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('robotics_dashboard.db')
    cursor = conn.cursor()
    
    # Get robot count by status
    cursor.execute('SELECT status, COUNT(*) FROM robots GROUP BY status')
    status_counts = dict(cursor.fetchall())
    
    # Get average battery level
    cursor.execute('SELECT AVG(battery_level) FROM robots')
    avg_battery = cursor.fetchone()[0] or 0
    
    # Get task count by status
    cursor.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
    task_counts = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'robot_status_counts': status_counts,
        'average_battery_level': round(avg_battery, 2),
        'task_status_counts': task_counts,
        'total_robots': sum(status_counts.values()),
        'total_tasks': sum(task_counts.values())
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 