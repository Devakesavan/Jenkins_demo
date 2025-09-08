from flask import Flask, render_template_string, jsonify, request
import os
import datetime
import psutil
import platform
import socket
import logging
from logging.handlers import RotatingFileHandler
import sys

app = Flask(__name__)

# Enhanced logging configuration
if not app.debug:
    file_handler = RotatingFileHandler('flask_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask application startup')

# HTML template with enhanced DevOps theme
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
            animation: pulse 2s ease-in-out infinite alternate;
        }
        
        @keyframes pulse {
            from { text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
            to { text-shadow: 4px 4px 8px rgba(0,0,0,0.5); }
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .status-banner {
            background: linear-gradient(45deg, #28a745, #20c997);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            animation: slideIn 1s ease-out;
        }
        
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
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
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #fff;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric strong {
            color: #FFD700;
            font-weight: 600;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            border-radius: 5px;
            transition: width 1s ease-out;
        }
        
        .network-info {
            background: rgba(0, 123, 255, 0.2);
            border-left: 4px solid #007bff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
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
            transition: all 0.3s ease;
        }
        
        .api-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #4ECDC4, #FF6B6B);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .deployment-info {
            background: rgba(108, 117, 125, 0.2);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 12px;
        }
    </style>
    <script>
        // Auto-refresh functionality
        let refreshInterval;
        let countdownInterval;
        let timeLeft = 30;
        
        function startAutoRefresh() {
            refreshInterval = setInterval(() => {
                location.reload();
            }, 30000);
            
            updateCountdown();
            countdownInterval = setInterval(updateCountdown, 1000);
        }
        
        function updateCountdown() {
            document.getElementById('countdown').textContent = timeLeft;
            timeLeft--;
            if (timeLeft < 0) {
                timeLeft = 30;
            }
        }
        
        function toggleAutoRefresh() {
            const button = document.getElementById('refresh-toggle');
            if (refreshInterval) {
                clearInterval(refreshInterval);
                clearInterval(countdownInterval);
                refreshInterval = null;
                button.textContent = 'Enable Auto-Refresh';
                document.getElementById('countdown-text').style.display = 'none';
            } else {
                startAutoRefresh();
                button.textContent = 'Disable Auto-Refresh';
                document.getElementById('countdown-text').style.display = 'inline';
            }
        }
        
        // Initialize auto-refresh on load
        window.onload = function() {
            startAutoRefresh();
            
            // Animate progress bars
            setTimeout(() => {
                const progressBars = document.querySelectorAll('.progress-fill');
                progressBars.forEach(bar => {
                    const width = bar.dataset.width;
                    bar.style.width = width + '%';
                });
            }, 500);
        }
    </script>
</head>
<body>
    <div class="auto-refresh">
        <button id="refresh-toggle" onclick="toggleAutoRefresh()" style="background: none; border: none; color: white; cursor: pointer;">Disable Auto-Refresh</button>
        <div id="countdown-text" style="margin-top: 5px;">Next refresh: <span id="countdown">30</span>s</div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps Monitoring Dashboard</h1>
            <p>Continuous Integration & Deployment Status</p>
            <div class="status-banner">
                <h2>✅ All Systems Operational - Deployed via Jenkins CI/CD</h2>
                <p>Last Updated: {{ app_status.current_time }}</p>
            </div>
        </div>
        
        <div class="network-info">
            <h4>🌐 Network Access Information</h4>
            <p><strong>Public URL:</strong> <a href="http://{{ network_info.public_ip }}:{{ app_status.port }}" target="_blank" style="color: #FFD700;">http://{{ network_info.public_ip }}:{{ app_status.port }}</a></p>
            <p><strong>Private URL:</strong> http://{{ network_info.private_ip }}:{{ app_status.port }}</p>
            <p><strong>Localhost:</strong> http://localhost:{{ app_status.port }}</p>
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
                    <span>Hostname:</span>
                    <strong>{{ system_info.hostname }}</strong>
                </div>
                <div class="metric">
                    <span>Python Version:</span>
                    <strong>{{ system_info.python_version }}</strong>
                </div>
                <div class="metric">
                    <span>Boot Time:</span>
                    <strong>{{ system_info.boot_time }}</strong>
                </div>
            </div>
            
            <div class="card">
                <h3>💾 Resource Usage</h3>
                <div class="metric">
                    <span>CPU Usage:</span>
                    <strong>{{ resources.cpu_percent }}%</strong>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" data-width="{{ resources.cpu_percent }}"></div>
                </div>
                
                <div class="metric">
                    <span>Memory Usage:</span>
                    <strong>{{ resources.memory_percent }}% ({{ resources.memory_used }}GB / {{ resources.memory_total }}GB)</strong>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" data-width="{{ resources.memory_percent }}"></div>
                </div>
                
                <div class="metric">
                    <span>Disk Usage:</span>
                    <strong>{{ resources.disk_percent }}% ({{ resources.disk_used }}GB / {{ resources.disk_total }}GB)</strong>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" data-width="{{ resources.disk_percent }}"></div>
                </div>
            </div>
            
            <div class="card">
                <h3>🚀 Application Status</h3>
                <div class="metric">
                    <span>Server Start Time:</span>
                    <strong>{{ app_status.start_time }}</strong>
                </div>
                <div class="metric">
                    <span>Current Time:</span>
                    <strong>{{ app_status.current_time }}</strong>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <strong>{{ app_status.uptime }}</strong>
                </div>
                <div class="metric">
                    <span>Environment:</span>
                    <strong>{{ app_status.environment }}</strong>
                </div>
                <div class="metric">
                    <span>Port:</span>
                    <strong>{{ app_status.port }}</strong>
                </div>
                <div class="metric">
                    <span>Process ID:</span>
                    <strong>{{ app_status.pid }}</strong>
                </div>
            </div>
            
            <div class="card">
                <h3>🔗 Network Information</h3>
                <div class="metric">
                    <span>Public IP:</span>
                    <strong>{{ network_info.public_ip }}</strong>
                </div>
                <div class="metric">
                    <span>Private IP:</span>
                    <strong>{{ network_info.private_ip }}</strong>
                </div>
                <div class="metric">
                    <span>Hostname:</span>
                    <strong>{{ network_info.hostname }}</strong>
                </div>
                <div class="metric">
                    <span>Port Status:</span>
                    <strong style="color: #28a745;">✅ Listening on {{ app_status.port }}</strong>
                </div>
            </div>
        </div>
        
        <div class="deployment-info">
            <h4>📋 Deployment Information</h4>
            <p><strong>Deployed via:</strong> Jenkins CI/CD Pipeline</p>
            <p><strong>Environment:</strong> {{ app_status.environment }}</p>
            <p><strong>Version:</strong> v1.2.0</p>
            <p><strong>Last Deployment:</strong> {{ app_status.current_time }}</p>
        </div>
        
        <div class="api-section">
            <h3>🔌 API Endpoints</h3>
            <a href="/api/health" class="api-button" target="_blank">Health Check</a>
            <a href="/api/system" class="api-button" target="_blank">System Info</a>
            <a href="/api/metrics" class="api-button" target="_blank">Metrics</a>
            <a href="/api/network" class="api-button" target="_blank">Network Info</a>
            <button class="api-button" onclick="location.reload()">🔄 Refresh Dashboard</button>
        </div>
        
        <div class="footer">
            <p>🔧 DevOps Flask Application | Monitoring Dashboard</p>
            <p>Deployed on {{ system_info.platform }} | Python {{ system_info.python_version }}</p>
            <p>© 2025 DevOps Team | Continuous Integration & Deployment</p>
        </div>
    </div>
</body>
</html>
'''

# Global variable to track start time
app_start_time = datetime.datetime.now()

def get_network_info():
    """Get network information including public and private IPs"""
    try:
        # Get private IP
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)
        
        # Try to get public IP using multiple methods
        public_ip = "Unknown"
        import subprocess
        try:
            result = subprocess.run(['curl', '-s', '--max-time', '3', 'http://checkip.amazonaws.com'], 
                                 capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                public_ip = result.stdout.strip()
        except:
            try:
                result = subprocess.run(['curl', '-s', '--max-time', '3', 'http://ipinfo.io/ip'], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    public_ip = result.stdout.strip()
            except:
                pass
        
        return {
            'public_ip': public_ip,
            'private_ip': private_ip,
            'hostname': hostname
        }
    except Exception as e:
        app.logger.error(f"Error getting network info: {str(e)}")
        return {
            'public_ip': 'Unknown',
            'private_ip': 'Unknown', 
            'hostname': 'Unknown'
        }

@app.route('/')
def dashboard():
    """Enhanced main dashboard route"""
    try:
        # System information
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        system_info = {
            'platform': platform.system() + " " + platform.release(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Resource usage
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            'cpu_percent': round(psutil.cpu_percent(interval=1), 1),
            'memory_percent': round(memory.percent, 1),
            'memory_used': round(memory.used / (1024**3), 2),
            'memory_total': round(memory.total / (1024**3), 2),
            'memory_available': round(memory.available / (1024**3), 2),
            'disk_percent': round(disk.percent, 1),
            'disk_used': round(disk.used / (1024**3), 2),
            'disk_total': round(disk.total / (1024**3), 2)
        }
        
        # Application status
        current_time = datetime.datetime.now()
        uptime = current_time - app_start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        app_status = {
            'start_time': app_start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'uptime': uptime_str,
            'environment': os.getenv('FLASK_ENV', 'production'),
            'port': os.getenv('PORT', '5000'),
            'pid': os.getpid()
        }
        
        # Network information
        network_info = get_network_info()
        
        return render_template_string(
            HTML_TEMPLATE,
            system_info=system_info,
            resources=resources,
            app_status=app_status,
            network_info=network_info
        )
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        return f"Dashboard Error: {str(e)}", 500

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test database connection, external services, etc. here
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'service': 'devops-flask-app',
            'version': '1.2.0',
            'uptime_seconds': (datetime.datetime.now() - app_start_time).total_seconds(),
            'environment': os.getenv('FLASK_ENV', 'production'),
            'port': os.getenv('PORT', '5000'),
            'pid': os.getpid(),
            'checks': {
                'memory': 'ok' if psutil.virtual_memory().percent < 90 else 'warning',
                'cpu': 'ok' if psutil.cpu_percent() < 80 else 'warning',
                'disk': 'ok' if psutil.disk_usage('/').percent < 85 else 'warning'
            }
        }
        return jsonify(health_status)
    except Exception as e:
        app.logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/system')
def system_info():
    """Enhanced system information API endpoint"""
    try:
        cpu_times = psutil.cpu_times()
        return jsonify({
            'platform': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_times': {
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle
            },
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'uptime_seconds': (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
        })
    except Exception as e:
        app.logger.error(f"System info error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics')
def metrics():
    """Enhanced system metrics API endpoint"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        
        # Get network I/O statistics
        net_io = psutil.net_io_counters()
        
        metrics_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free,
                'cached': memory.cached if hasattr(memory, 'cached') else 0
            },
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            },
            'processes': len(psutil.pids()),
            'uptime_seconds': (datetime.datetime.now() - app_start_time).total_seconds()
        }
        
        return jsonify(metrics_data)
    except Exception as e:
        app.logger.error(f"Metrics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/network')
def network_info():
    """Network information API endpoint"""
    try:
        network_data = get_network_info()
        
        # Add additional network info
        try:
            network_data['interfaces'] = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        network_data['interfaces'].append({
                            'interface': interface,
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })
        except:
            pass
            
        return jsonify(network_data)
    except Exception as e:
        app.logger.error(f"Network info error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get application logs"""
    try:
        log_lines = request.args.get('lines', 50, type=int)
        log_file = 'flask_app.log'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-log_lines:] if len(lines) > log_lines else lines
                return jsonify({
                    'logs': [line.strip() for line in recent_lines],
                    'total_lines': len(lines),
                    'requested_lines': log_lines
                })
        else:
            return jsonify({
                'logs': ['No log file found'],
                'total_lines': 0,
                'requested_lines': log_lines
            })
    except Exception as e:
        app.logger.error(f"Logs error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Utility functions for testing
def add_numbers(a, b):
    """Simple function for testing purposes"""
    return a + b

def multiply_numbers(a, b):
    """Another function for testing"""
    return a * b

def get_deployment_status():
    """Function to simulate deployment status check"""
    return {
        'status': 'deployed',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'version': '1.2.0',
        'deployment_time': datetime.datetime.now().isoformat(),
        'health': 'good'
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'status_code': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'status_code': 500}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.logger.info(f'Starting Flask app on {host}:{port}')
    app.logger.info(f'Environment: {os.environ.get("FLASK_ENV", "production")}')
    app.logger.info(f'Debug mode: {debug}')
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except Exception as e:
        app.logger.error(f'Failed to start Flask app: {str(e)}')
        sys.exit(1)
