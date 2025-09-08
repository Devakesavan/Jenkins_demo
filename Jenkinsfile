pipeline {
    agent any
    environment {
        APP_PORT = '3000'  // Changed from 3000
        VENV_DIR = '.venv'
        FLASK_HOST = '0.0.0.0'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/Devakesavan/Jenkins_demo.git',
                    branch: 'main',
                    credentialsId: 'github-credentials'
            }
        }
        stage('Setup VirtualEnv') {
            steps {
                echo "Creating Python virtual environment..."
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    fi
                '''
            }
        }
        stage('Build') {
            steps {
                echo "Running build script..."
                sh '''
                    . ${VENV_DIR}/bin/activate
                    chmod +x build.sh
                    ./build.sh
                '''
            }
        }
        stage('Test') {
            steps {
                echo "Running test script..."
                sh '''
                    . ${VENV_DIR}/bin/activate
                    chmod +x test.sh
                    ./test.sh
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo "Deploying Flask app..."
                sh '''
                    echo "Stopping any existing Flask process..."
                    pkill -f "python.*app.py" || true
                    sleep 2
                    
                    echo "Starting Flask app on ${FLASK_HOST}:${APP_PORT}..."
                    . ${VENV_DIR}/bin/activate
                    export PORT=${APP_PORT}
                    export FLASK_ENV=production
                    export FLASK_HOST=${FLASK_HOST}
                    
                    # Start the app in background
                    nohup python app.py > flask.log 2>&1 &
                    
                    # Wait a bit and check if it started
                    sleep 3
                    
                    if pgrep -f "python.*app.py" > /dev/null; then
                        echo "✅ Flask app started successfully!"
                        echo "📝 Process ID: $(pgrep -f 'python.*app.py')"
                        echo "🌐 Application should be accessible at: http://$(hostname -I | awk '{print $1}'):${APP_PORT}"
                        echo "📋 Check logs with: tail -f ${WORKSPACE}/flask.log"
                    else
                        echo "❌ Failed to start Flask app!"
                        echo "Last few lines from log:"
                        tail -10 flask.log || echo "No log file found"
                        exit 1
                    fi
                '''
            }
        }
        stage('Health Check') {
            steps {
                echo "Performing health check..."
                sh '''
                    sleep 5
                    
                    # Test local connectivity
                    if curl -f -s http://localhost:${APP_PORT}/ > /dev/null; then
                        echo "✅ Local health check passed"
                    else
                        echo "❌ Local health check failed"
                        echo "App logs:"
                        tail -20 flask.log
                        exit 1
                    fi
                '''
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
            sh '''
                echo "=== Deployment Summary ==="
                echo "Workspace: ${WORKSPACE}"
                echo "App Port: ${APP_PORT}"
                echo "Process Status:"
                ps aux | grep "python.*app.py" | grep -v grep || echo "No Flask process found"
                echo "Port Status:"
                netstat -tlnp | grep :${APP_PORT} || echo "Port ${APP_PORT} not listening"
            '''
        }
        success {
            echo 'Pipeline succeeded ✅'
        }
        failure {
            echo 'Pipeline failed ❌'
            sh '''
                echo "=== Failure Debug Info ==="
                echo "Flask logs:"
                tail -50 flask.log || echo "No flask.log found"
                echo "System processes:"
                ps aux | grep python
            '''
        }
    }
}
