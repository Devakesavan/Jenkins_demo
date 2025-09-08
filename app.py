from flask import Flask, jsonify, render_template_string
import os

app = Flask(__name__)

# HTML template for the home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Flask CI/CD Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .endpoints { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .endpoint { margin: 10px 0; padding: 8px; background: white; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Flask CI/CD Pipeline Demo</h1>
        <div class="status">
            <strong>✅ Application is running successfully!</strong>
            <br>Version: 1.0.0
            <br>Environment: {{ env }}
        </div>
        <div class="endpoints">
            <h3>Available Endpoints:</h3>
            <div class="endpoint"><strong>GET /</strong> - This home page</div>
            <div class="endpoint"><strong>GET /health</strong> - Health check endpoint</div>
            <div class="endpoint"><strong>GET /api/status</strong> - API status in JSON</div>
            <div class="endpoint"><strong>GET /api/info</strong> - Application information</div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page"""
    env = os.environ.get('FLASK_ENV', 'development')
    return render_template_string(HOME_TEMPLATE, env=env)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'message': 'Application is running properly',
        'version': '1.0.0'
    }), 200

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_status': 'active',
        'endpoints_available': 4,
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'python_version': os.sys.version.split()[0]
    })

@app.route('/api/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        'app_name': 'Flask CI/CD Demo',
        'version': '1.0.0',
        'description': 'Sample Flask application for Jenkins CI/CD pipeline demonstration',
        'author': 'DevOps Team',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Home page'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/api/status', 'method': 'GET', 'description': 'API status'},
            {'path': '/api/info', 'method': 'GET', 'description': 'App information'}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred',
        'status_code': 500
    }), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Flask application on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
