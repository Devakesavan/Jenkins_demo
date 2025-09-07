from flask import Flask, render_template_string, jsonify
import os
import datetime
import psutil
import platform

app = Flask(__name__)

# HTML template with DevOps theme
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #fff;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
        }
        
        .metric strong {
            color: #FFD700;
        }
        
        .status {
            text-align: center;
            padding: 20px;
            background: rgba(0, 255, 0, 0.2);
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .status.healthy {
            background: rgba(0, 255, 0, 0.2);
        }
        
        .api-section {
            margin-top: 30px;
            text-align: center;
        }
        
        .api-button {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: transform 0.3s ease;
        }
        
        .api-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps Monitoring Dashboard</h1>
            <p>Continuous Integration & Deployment Status</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>📊 System Information</h3>
                <div class="metric">
                    <span>Platform:</span>
                    <strong>{{ system_info.platform }}</strong>
                </div>
                <div class="metric">
                    <span>Architecture:</span>
                    <strong>{{ system_info.architecture }}</strong>
                </div>
                <div class="metric">
                    <span>Processor:</span>
                    <strong>{{ system_info.processor }}</strong>
                </div>
                <div class="metric">
                    <span>Python Version:</span>
                    <strong>{{ system_info.python_version }}</strong>
                </div>
            </div>
            
            <div class="card">
                <h3>💾 Resource Usage</h3>
                <div class="metric">
                    <span>CPU Usage:</span>
                    <strong>{{ resources.cpu_percent }}%</strong>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <strong>{{ resources.memory_percent }}%</strong>
                </div>
                <div class="metric">
                    <span>Available Memory:</span>
                    <strong>{{ resources.memory_available }} GB</strong>
                </div>
                <div class="metric">
                    <span>Disk Usage:</span>
                    <strong>{{ resources.disk_percent }}%</strong>
                </div>
            </div>
            
            <div class="card">
                <h3>🕒 Application Status</h3>
                <div class="metric">
                    <span>Server Start Time:</span>
                    <strong>{{ app_status.start_time }}</strong>
                </div>
                <div class="metric">
                    <span>Current Time:</span>
                    <strong>{{ app_status.current_time }}</strong>
                </div>
                <div class="metric">
                    <span>Environment:</span>
                    <strong>{{ app_status.environment }}</strong>
                </div>
                <div class="metric">
                    <span>Port:</span>
                    <strong>{{ app_status.port }}</strong>
                </div>
            </div>
        </div>
        
        <div class="status healthy">
            <h2>✅ All Systems Operational</h2>
            <p>Your DevOps pipeline is running smoothly!</p>
        </div>
        
        <div class="api-section">
            <h3>API Endpoints</h3>
            <a href="/api/health" class="api-button">Health Check</a>
            <a href="/api/system" class="api-button">System Info</a>
            <a href="/api/metrics" class="api-button">Metrics</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Main dashboard route"""
    try:
        # System information
        system_info = {
            'platform': platform.system() + " " + platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor() or "Unknown",
            'python_version': platform.python_version()
        }
        
        # Resource usage
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            'cpu_percent': round(psutil.cpu_percent(interval=1), 1),
            'memory_percent': round(memory.percent, 1),
            'memory_available': round(memory.available / (1024**3), 2),
            'disk_percent': round(disk.percent, 1)
        }
        
        # Application status
        app_status = {
            'start_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'environment': os.getenv('FLASK_ENV', 'production'),
            'port': os.getenv('PORT', '5000')
        }
        
        return render_template_string(
            HTML_TEMPLATE,
            system_info=system_info,
            resources=resources,
            app_status=app_status
        )
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'devops-flask-app',
        'version': '1.0.0'
    })

@app.route('/api/system')
def system_info():
    """System information API endpoint"""
    try:
        return jsonify({
            'platform': platform.system(),
            'release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def metrics():
    """System metrics API endpoint"""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'timestamp': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def add_numbers(a, b):
    """Simple function for testing purposes"""
    return a + b

def get_deployment_status():
    """Function to simulate deployment status check"""
    return {
        'status': 'deployed',
        'environment': 'production',
        'version': '1.0.0'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
