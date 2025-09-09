from flask import Flask, jsonify, request, render_template_string
import os
import logging
import datetime
import socket
import json
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    ENV = os.environ.get('FLASK_ENV', 'production')
    VERSION = os.environ.get('APP_VERSION', '1.0.0')
    BUILD_NUMBER = os.environ.get('BUILD_NUMBER', 'local')
    GIT_COMMIT = os.environ.get('GIT_COMMIT', 'unknown')

app.config.from_object(Config)

# In-memory storage for demo purposes
app_data = {
    'deployments': [],
    'health_checks': 0,
    'requests_count': 0
}

# Middleware to count requests
@app.before_request
def before_request():
    app_data['requests_count'] += 1
    logger.info(f"Request {app_data['requests_count']}: {request.method} {request.path}")

# Helper decorator for JSON responses
def json_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            return jsonify(result)
        return result
    return wrapper

# HTML template for the main page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask CI/CD Demo App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: #f0f8ff; padding: 15px; border-radius: 5px; text-align: center; }
        .endpoints { background: #fff8f0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .endpoint { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #007acc; }
        .success { color: #28a745; }
        .info { color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Flask CI/CD Demo Application</h1>
            <p class="success">✅ Successfully deployed via Jenkins Pipeline!</p>
        </div>
        
        <div class="status">
            <h3>📊 Application Status</h3>
            <p><strong>Version:</strong> {{ version }}</p>
            <p><strong>Build:</strong> #{{ build_number }}</p>
            <p><strong>Environment:</strong> {{ env }}</p>
            <p><strong>Server:</strong> {{ hostname }}</p>
            <p><strong>Uptime:</strong> {{ uptime }}</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <h4>Health Checks</h4>
                <div style="font-size: 24px; color: #28a745;">{{ health_checks }}</div>
            </div>
            <div class="metric">
                <h4>Total Requests</h4>
                <div style="font-size: 24px; color: #007bff;">{{ requests }}</div>
            </div>
            <div class="metric">
                <h4>Deployments</h4>
                <div style="font-size: 24px; color: #6f42c1;">{{ deployments }}</div>
            </div>
        </div>

        <div class="endpoints">
            <h3>🔗 Available API Endpoints</h3>
            <div class="endpoint">
                <strong>GET /</strong> - This main page
            </div>
            <div class="endpoint">
                <strong>GET /health</strong> - Health check endpoint
            </div>
            <div class="endpoint">
                <strong>GET /api/status</strong> - Application status API
            </div>
            <div class="endpoint">
                <strong>GET /api/metrics</strong> - Application metrics
            </div>
            <div class="endpoint">
                <strong>POST /api/deploy</strong> - Record deployment (for pipeline)
            </div>
            <div class="endpoint">
                <strong>GET /api/info</strong> - System information
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    """Main application page with dashboard"""
    return render_template_string(HTML_TEMPLATE,
        version=app.config['VERSION'],
        build_number=app.config['BUILD_NUMBER'],
        env=app.config['ENV'],
        hostname=socket.gethostname(),
        uptime="Running",
        health_checks=app_data['health_checks'],
        requests=app_data['requests_count'],
        deployments=len(app_data['deployments'])
    )

@app.route("/health")
@json_response
def health_check():
    """Health check endpoint for load balancers and monitoring"""
    app_data['health_checks'] += 1
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": app.config['VERSION'],
        "build": app.config['BUILD_NUMBER'],
        "checks": {
            "application": "ok",
            "database": "ok",  # Would be actual DB check in real app
            "external_services": "ok"
        }
    }
    
    logger.info(f"Health check #{app_data['health_checks']} - Status: healthy")
    return health_status

@app.route("/api/status")
@json_response
def api_status():
    """Detailed application status"""
    return {
        "application": "Flask CI/CD Demo",
        "status": "running",
        "version": app.config['VERSION'],
        "build_number": app.config['BUILD_NUMBER'],
        "git_commit": app.config['GIT_COMMIT'],
        "environment": app.config['ENV'],
        "server_info": {
            "hostname": socket.gethostname(),
            "python_version": os.sys.version.split()[0]
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.route("/api/metrics")
@json_response
def api_metrics():
    """Application metrics endpoint"""
    return {
        "metrics": {
            "total_requests": app_data['requests_count'],
            "health_checks": app_data['health_checks'],
            "deployments_count": len(app_data['deployments']),
            "uptime_seconds": 3600,  # Would be actual uptime calculation
            "memory_usage": "45MB",  # Would be actual memory usage
            "cpu_usage": "2.5%"      # Would be actual CPU usage
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.route("/api/deploy", methods=['POST'])
@json_response
def record_deployment():
    """Record deployment information (called by Jenkins pipeline)"""
    deployment_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "build_number": request.json.get('build_number', app.config['BUILD_NUMBER']) if request.is_json else app.config['BUILD_NUMBER'],
        "version": request.json.get('version', app.config['VERSION']) if request.is_json else app.config['VERSION'],
        "git_commit": request.json.get('git_commit', app.config['GIT_COMMIT']) if request.is_json else app.config['GIT_COMMIT'],
        "deployed_by": "Jenkins CI/CD Pipeline"
    }
    
    app_data['deployments'].append(deployment_data)
    logger.info(f"New deployment recorded: Build #{deployment_data['build_number']}")
    
    return {
        "message": "Deployment recorded successfully",
        "deployment": deployment_data,
        "total_deployments": len(app_data['deployments'])
    }

@app.route("/api/deployments")
@json_response
def get_deployments():
    """Get deployment history"""
    return {
        "deployments": app_data['deployments'][-10:],  # Last 10 deployments
        "total_count": len(app_data['deployments'])
    }

@app.route("/api/info")
@json_response
def system_info():
    """System information endpoint"""
    return {
        "system": {
            "hostname": socket.gethostname(),
            "platform": os.name,
            "python_version": os.sys.version,
            "flask_version": "2.x",
            "environment_variables": {
                "FLASK_ENV": os.environ.get('FLASK_ENV', 'not set'),
                "APP_VERSION": os.environ.get('APP_VERSION', 'not set'),
                "BUILD_NUMBER": os.environ.get('BUILD_NUMBER', 'not set')
            }
        },
        "application": {
            "name": "Flask CI/CD Demo",
            "version": app.config['VERSION'],
            "build": app.config['BUILD_NUMBER'],
            "git_commit": app.config['GIT_COMMIT']
        }
    }

@app.route("/test")
@json_response
def test_endpoint():
    """Test endpoint for automated testing"""
    return {
        "test": "success",
        "message": "Test endpoint is working correctly",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "request_count": app_data['requests_count']
    }

# Error handlers
@app.errorhandler(404)
@json_response
def not_found(error):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }, 404

@app.errorhandler(500)
@json_response
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return {
        "error": "Internal Server Error",
        "message": "An internal error occurred",
        "status_code": 500
    }, 500

if __name__ == "__main__":
    logger.info("Starting Flask CI/CD Demo Application")
    logger.info(f"Version: {app.config['VERSION']}")
    logger.info(f"Build: {app.config['BUILD_NUMBER']}")
    logger.info(f"Environment: {app.config['ENV']}")
    
    # Get port from environment variable (useful for deployment)
    port = int(os.environ.get('PORT', 5000))
    debug = app.config['ENV'] == 'development'
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
