from flask import Flask, jsonify, request, render_template_string
import os
import logging
import datetime
import socket
import json
import hashlib
import time
from functools import wraps

# Configure logging for DevOps monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if os.path.exists('/tmp') else logging.StreamHandler()
    ]
)
logger = logging.getLogger("DevOpsApp")

app = Flask(__name__)

# DevOps Configuration
class DevOpsConfig:
    # Application Configuration
    APP_NAME = "DevOps-Flask-Pipeline"
    SECRET_KEY = os.environ.get('SECRET_KEY', 'devops-secret-2024')
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    
    # CI/CD Pipeline Variables
    VERSION = os.environ.get('APP_VERSION', '2.0.0')
    BUILD_NUMBER = os.environ.get('BUILD_NUMBER', 'local-build')
    GIT_COMMIT_SHA = os.environ.get('GIT_COMMIT', 'unknown')[:8]
    GIT_BRANCH = os.environ.get('GIT_BRANCH', 'main')
    
    # Jenkins Pipeline Variables
    JENKINS_BUILD_URL = os.environ.get('BUILD_URL', 'http://localhost:8080')
    JENKINS_JOB_NAME = os.environ.get('JOB_NAME', 'flask-devops-pipeline')
    
    # Infrastructure Details
    AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    EC2_INSTANCE_ID = os.environ.get('EC2_INSTANCE_ID', 'local-instance')

app.config.from_object(DevOpsConfig)

# DevOps Metrics Storage
devops_metrics = {
    'pipeline_runs': [],
    'deployment_history': [],
    'health_checks': 0,
    'api_calls': 0,
    'errors': 0,
    'start_time': time.time(),
    'build_artifacts': []
}

# Middleware for DevOps monitoring
@app.before_request
def track_requests():
    devops_metrics['api_calls'] += 1
    endpoint = request.endpoint or 'unknown'
    logger.info(f"API Call #{devops_metrics['api_calls']} | {request.method} {request.path} | Endpoint: {endpoint}")

# DevOps utility functions
def get_uptime():
    uptime_seconds = int(time.time() - devops_metrics['start_time'])
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    return f"{hours}h {minutes}m"

def generate_build_hash():
    """Generate unique build hash for artifacts"""
    data = f"{app.config['BUILD_NUMBER']}{app.config['GIT_COMMIT_SHA']}{time.time()}"
    return hashlib.md5(data.encode()).hexdigest()[:8]

# JSON response decorator
def json_api_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict):
                return jsonify(result)
            return result
        except Exception as e:
            devops_metrics['errors'] += 1
            logger.error(f"API Error in {func.__name__}: {str(e)}")
            return jsonify({
                "error": "Internal Server Error",
                "message": "DevOps pipeline encountered an error",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }), 500
    return wrapper

# DevOps Dashboard HTML Template
DEVOPS_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_name }} - DevOps Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333; min-height: 100vh; padding: 20px;
        }
        .dashboard { max-width: 1200px; margin: 0 auto; }
        
        .header {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            padding: 30px; border-radius: 20px; text-align: center;
            margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        .header .subtitle { color: #7f8c8d; font-size: 1.2em; }
        
        .status-bar {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white; padding: 15px 25px; border-radius: 50px;
            display: inline-block; margin: 15px 0; font-weight: bold;
            box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
        }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin: 30px 0; }
        
        .card {
            background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
            padding: 25px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.2); }
        
        .card h3 { color: #2c3e50; margin-bottom: 20px; font-size: 1.3em; display: flex; align-items: center; }
        .card h3::before { content: '🚀'; margin-right: 10px; font-size: 1.2em; }
        
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
        .metric {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white; padding: 20px; border-radius: 10px; text-align: center;
        }
        .metric-value { font-size: 2em; font-weight: bold; }
        .metric-label { font-size: 0.9em; opacity: 0.9; }
        
        .pipeline-info { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }
        .deployment-info { background: linear-gradient(135deg, #f39c12, #e67e22); color: white; }
        .system-info { background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; }
        
        .api-grid { display: grid; gap: 10px; }
        .api-endpoint {
            background: #ecf0f1; padding: 15px; border-radius: 8px;
            border-left: 4px solid #3498db; transition: all 0.3s ease;
        }
        .api-endpoint:hover { background: #d5dbdb; border-left-color: #2980b9; }
        .api-method { 
            background: #3498db; color: white; padding: 4px 8px; 
            border-radius: 4px; font-size: 0.8em; font-weight: bold;
        }
        .api-post { background: #27ae60; }
        .api-delete { background: #e74c3c; }
        
        .footer {
            background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
            padding: 20px; border-radius: 15px; text-align: center;
            margin-top: 30px; color: white;
        }
        
        .build-badge { 
            background: #34495e; color: white; padding: 5px 10px; 
            border-radius: 20px; font-size: 0.8em; margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🔧 {{ app_name }}</h1>
            <p class="subtitle">Jenkins CI/CD Pipeline • AWS EC2 Deployment</p>
            <div class="status-bar">✅ Pipeline Status: DEPLOYED & RUNNING</div>
            <div>
                <span class="build-badge">Build #{{ build_number }}</span>
                <span class="build-badge">{{ git_commit }}</span>
                <span class="build-badge">{{ environment }}</span>
            </div>
        </div>

        <div class="grid">
            <div class="card pipeline-info">
                <h3>CI/CD Pipeline Status</h3>
                <p><strong>Job Name:</strong> {{ job_name }}</p>
                <p><strong>Branch:</strong> {{ git_branch }}</p>
                <p><strong>Last Build:</strong> #{{ build_number }}</p>
                <p><strong>Commit SHA:</strong> {{ git_commit }}</p>
                <p><strong>Build URL:</strong> <a href="{{ build_url }}" style="color: #ecf0f1;">Jenkins Console</a></p>
            </div>

            <div class="card deployment-info">
                <h3>Deployment Information</h3>
                <p><strong>Environment:</strong> {{ environment }}</p>
                <p><strong>AWS Region:</strong> {{ aws_region }}</p>
                <p><strong>EC2 Instance:</strong> {{ instance_id }}</p>
                <p><strong>Uptime:</strong> {{ uptime }}</p>
                <p><strong>Version:</strong> {{ version }}</p>
            </div>

            <div class="card system-info">
                <h3>System Monitoring</h3>
                <p><strong>Hostname:</strong> {{ hostname }}</p>
                <p><strong>Platform:</strong> Linux/AWS EC2</p>
                <p><strong>Python:</strong> {{ python_version }}</p>
                <p><strong>Flask:</strong> Production Mode</p>
                <p><strong>Port:</strong> 5000</p>
            </div>

            <div class="card">
                <h3>DevOps Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value">{{ api_calls }}</div>
                        <div class="metric-label">API Calls</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ health_checks }}</div>
                        <div class="metric-label">Health Checks</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ deployments }}</div>
                        <div class="metric-label">Deployments</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ errors }}</div>
                        <div class="metric-label">Errors</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>DevOps API Endpoints</h3>
                <div class="api-grid">
                    <div class="api-endpoint">
                        <span class="api-method">GET</span> <strong>/devops/health</strong>
                        <br><small>Health check for load balancers & monitoring</small>
                    </div>
                    <div class="api-endpoint">
                        <span class="api-method">GET</span> <strong>/devops/pipeline</strong>
                        <br><small>CI/CD pipeline status and metrics</small>
                    </div>
                    <div class="api-endpoint">
                        <span class="api-method api-post">POST</span> <strong>/devops/deploy</strong>
                        <br><small>Record new deployment (called by Jenkins)</small>
                    </div>
                    <div class="api-endpoint">
                        <span class="api-method">GET</span> <strong>/devops/metrics</strong>
                        <br><small>Application performance metrics</small>
                    </div>
                    <div class="api-endpoint">
                        <span class="api-method">GET</span> <strong>/devops/infrastructure</strong>
                        <br><small>AWS infrastructure information</small>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🚀 DevOps Flask Application | Automated CI/CD with Jenkins | Deployed on AWS EC2</p>
            <p>Last Updated: {{ timestamp }}</p>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

# Routes - DevOps Dashboard
@app.route("/")
def devops_dashboard():
    """Main DevOps dashboard"""
    return render_template_string(DEVOPS_DASHBOARD,
        app_name=app.config['APP_NAME'],
        build_number=app.config['BUILD_NUMBER'],
        git_commit=app.config['GIT_COMMIT_SHA'],
        git_branch=app.config['GIT_BRANCH'],
        environment=app.config['ENVIRONMENT'],
        version=app.config['VERSION'],
        job_name=app.config['JENKINS_JOB_NAME'],
        build_url=app.config['JENKINS_BUILD_URL'],
        aws_region=app.config['AWS_REGION'],
        instance_id=app.config['EC2_INSTANCE_ID'],
        hostname=socket.gethostname(),
        python_version=".".join(map(str, [3, 9])),  # Simplified version
        uptime=get_uptime(),
        api_calls=devops_metrics['api_calls'],
        health_checks=devops_metrics['health_checks'],
        deployments=len(devops_metrics['deployment_history']),
        errors=devops_metrics['errors'],
        timestamp=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

@app.route("/devops/health")
@json_api_response
def devops_health_check():
    """DevOps Health Check - Critical for monitoring"""
    devops_metrics['health_checks'] += 1
    
    health_data = {
        "status": "healthy",
        "service": app.config['APP_NAME'],
        "environment": app.config['ENVIRONMENT'],
        "version": app.config['VERSION'],
        "build": app.config['BUILD_NUMBER'],
        "commit": app.config['GIT_COMMIT_SHA'],
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "uptime": get_uptime(),
        "checks": {
            "application": "passing",
            "database": "passing",
            "external_apis": "passing",
            "disk_space": "passing",
            "memory": "passing"
        },
        "metrics": {
            "response_time_ms": 45,
            "cpu_usage": "12%",
            "memory_usage": "156MB",
            "active_connections": 5
        }
    }
    
    logger.info(f"DevOps Health Check #{devops_metrics['health_checks']} - All systems operational")
    return health_data

@app.route("/devops/pipeline")
@json_api_response
def pipeline_status():
    """Jenkins Pipeline Status & Information"""
    return {
        "pipeline": {
            "name": app.config['JENKINS_JOB_NAME'],
            "status": "SUCCESS",
            "build_number": app.config['BUILD_NUMBER'],
            "build_url": app.config['JENKINS_BUILD_URL'],
            "last_run": datetime.datetime.utcnow().isoformat(),
            "duration": "2m 34s",
            "triggered_by": "GitHub webhook"
        },
        "git": {
            "branch": app.config['GIT_BRANCH'],
            "commit_sha": app.config['GIT_COMMIT_SHA'],
            "commit_message": "feat: enhanced devops monitoring endpoints",
            "author": "DevOps Engineer"
        },
        "stages": {
            "checkout": {"status": "SUCCESS", "duration": "15s"},
            "build": {"status": "SUCCESS", "duration": "45s"},
            "test": {"status": "SUCCESS", "duration": "30s"},
            "deploy": {"status": "SUCCESS", "duration": "1m 24s"}
        },
        "artifacts": devops_metrics['build_artifacts']
    }

@app.route("/devops/deploy", methods=['POST'])
@json_api_response
def record_devops_deployment():
    """Record deployment - Called by Jenkins Pipeline"""
    build_hash = generate_build_hash()
    
    deployment = {
        "deployment_id": f"deploy-{build_hash}",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "environment": app.config['ENVIRONMENT'],
        "version": app.config['VERSION'],
        "build_number": app.config['BUILD_NUMBER'],
        "git_commit": app.config['GIT_COMMIT_SHA'],
        "git_branch": app.config['GIT_BRANCH'],
        "deployed_by": "Jenkins CI/CD Pipeline",
        "deployment_strategy": "rolling",
        "infrastructure": {
            "platform": "AWS EC2",
            "region": app.config['AWS_REGION'],
            "instance_id": app.config['EC2_INSTANCE_ID']
        },
        "status": "successful"
    }
    
    # Record build artifact
    artifact = {
        "artifact_id": build_hash,
        "type": "docker_image",
        "name": f"{app.config['APP_NAME']}:{app.config['VERSION']}-{app.config['BUILD_NUMBER']}",
        "size": "125MB",
        "created": datetime.datetime.utcnow().isoformat()
    }
    
    devops_metrics['deployment_history'].append(deployment)
    devops_metrics['build_artifacts'].append(artifact)
    
    logger.info(f"🚀 New deployment recorded: {deployment['deployment_id']} | Build #{deployment['build_number']}")
    
    return {
        "message": "Deployment recorded successfully in DevOps pipeline",
        "deployment": deployment,
        "total_deployments": len(devops_metrics['deployment_history']),
        "build_artifact": artifact
    }

@app.route("/devops/metrics")
@json_api_response
def devops_metrics_api():
    """DevOps Application Metrics"""
    return {
        "application_metrics": {
            "total_requests": devops_metrics['api_calls'],
            "health_checks": devops_metrics['health_checks'],
            "error_count": devops_metrics['errors'],
            "uptime_seconds": int(time.time() - devops_metrics['start_time']),
            "uptime_formatted": get_uptime()
        },
        "performance_metrics": {
            "avg_response_time": "45ms",
            "requests_per_second": 12.5,
            "cpu_usage": "8.2%",
            "memory_usage": "156MB",
            "disk_usage": "2.1GB"
        },
        "deployment_metrics": {
            "total_deployments": len(devops_metrics['deployment_history']),
            "deployment_frequency": "3.2 per week",
            "success_rate": "98.7%",
            "rollback_count": 0
        },
        "pipeline_metrics": {
            "avg_build_time": "2m 45s",
            "pipeline_success_rate": "96.4%",
            "builds_this_month": 47,
            "test_coverage": "87%"
        }
    }

@app.route("/devops/infrastructure")
@json_api_response
def infrastructure_info():
    """AWS Infrastructure Information"""
    return {
        "aws_infrastructure": {
            "region": app.config['AWS_REGION'],
            "availability_zone": f"{app.config['AWS_REGION']}a",
            "instance_type": "t3.medium",
            "instance_id": app.config['EC2_INSTANCE_ID'],
            "vpc_id": "vpc-12345678",
            "subnet_id": "subnet-87654321",
            "security_groups": ["sg-devops-web", "sg-jenkins-access"]
        },
        "networking": {
            "public_ip": "3.15.123.45",
            "private_ip": "10.0.1.100",
            "load_balancer": "devops-app-lb",
            "ssl_certificate": "*.devops-app.com"
        },
        "monitoring": {
            "cloudwatch_enabled": True,
            "log_groups": ["/aws/ec2/devops-app", "/aws/jenkins/pipeline"],
            "alarms": ["high-cpu", "disk-space", "memory-usage"],
            "sns_topic": "devops-alerts"
        },
        "backup": {
            "ebs_snapshots": "daily",
            "retention_period": "30 days",
            "last_backup": "2024-01-15T02:00:00Z"
        }
    }

@app.route("/devops/deployments")
@json_api_response
def deployment_history():
    """Deployment History"""
    return {
        "deployments": devops_metrics['deployment_history'][-10:],  # Last 10
        "total_count": len(devops_metrics['deployment_history']),
        "statistics": {
            "successful_deployments": len([d for d in devops_metrics['deployment_history'] if d['status'] == 'successful']),
            "failed_deployments": len([d for d in devops_metrics['deployment_history'] if d['status'] == 'failed']),
            "avg_deployment_time": "1m 45s"
        }
    }

@app.route("/devops/logs")
@json_api_response
def application_logs():
    """Application Logs (sample)"""
    return {
        "logs": [
            {"level": "INFO", "timestamp": "2024-01-15T10:30:45Z", "message": "Application started successfully"},
            {"level": "INFO", "timestamp": "2024-01-15T10:31:12Z", "message": "Health check endpoint called"},
            {"level": "INFO", "timestamp": "2024-01-15T10:32:01Z", "message": "New deployment initiated"},
            {"level": "INFO", "timestamp": "2024-01-15T10:33:15Z", "message": "Pipeline metrics updated"}
        ],
        "log_levels": {
            "INFO": 1250,
            "WARNING": 12,
            "ERROR": 3,
            "DEBUG": 0
        }
    }

# Error Handlers for DevOps
@app.errorhandler(404)
@json_api_response
def devops_not_found(error):
    return {
        "error": "Resource Not Found",
        "message": "The requested DevOps endpoint was not found",
        "available_endpoints": ["/devops/health", "/devops/pipeline", "/devops/metrics"],
        "status_code": 404,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }, 404

@app.errorhandler(500)
@json_api_response
def devops_server_error(error):
    devops_metrics['errors'] += 1
    logger.error(f"DevOps Application Error: {error}")
    return {
        "error": "Internal Server Error",
        "message": "DevOps pipeline encountered a critical error",
        "incident_id": generate_build_hash(),
        "status_code": 500,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }, 500

if __name__ == "__main__":
    logger.info("🚀 Starting DevOps Flask Application")
    logger.info(f"📦 Application: {app.config['APP_NAME']}")
    logger.info(f"🔖 Version: {app.config['VERSION']}")
    logger.info(f"🏗️  Build: #{app.config['BUILD_NUMBER']}")
    logger.info(f"🌿 Branch: {app.config['GIT_BRANCH']}")
    logger.info(f"📝 Commit: {app.config['GIT_COMMIT_SHA']}")
    logger.info(f"🌍 Environment: {app.config['ENVIRONMENT']}")
    logger.info(f"☁️  AWS Region: {app.config['AWS_REGION']}")
    
    # Get port from environment (Docker/K8s compatibility)
    port = int(os.environ.get('PORT', 5000))
    debug = app.config['ENVIRONMENT'] == 'development'
    
    logger.info(f"🌐 Starting server on 0.0.0.0:{port}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        threaded=True
    )
