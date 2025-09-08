pipeline {
    agent any
    environment {
        APP_PORT = '5000'
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
                    
                    # Method 1: Use screen to run in detached session
                    screen -dmS flask-app bash -c "cd ${WORKSPACE} && . ${VENV_DIR}/bin/activate && python app.py > flask.log 2>&1"
                    
                    # Wait and verify it started
                    sleep 5
                    
                    if pgrep -f "python.*app.py" > /dev/null; then
                        echo "✅ Flask app started successfully!"
                        echo "📝 Process ID: $(pgrep -f 'python.*app.py')"
                        echo "🌐 Application should be accessible at:"
                        
                        # Get IP addresses
                        PRIVATE_IP=$(hostname -I | awk '{print $1}')
                        PUBLIC_IP=$(curl -s --max-time 3 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "Not Available")
                        
                        echo "  Private: http://$PRIVATE_IP:${APP_PORT}"
                        if [ "$PUBLIC_IP" != "Not Available" ]; then
                            echo "  Public: http://$PUBLIC_IP:${APP_PORT}"
                        fi
                        
                        echo "📋 Check logs with: tail -f ${WORKSPACE}/flask.log"
                        echo "📋 Check screen session: screen -r flask-app"
                    else
                        echo "❌ Flask app failed to start!"
                        echo "Trying alternative method..."
                        
                        # Method 2: Use systemd-run if available
                        if command -v systemd-run >/dev/null 2>&1; then
                            echo "Using systemd-run..."
                            systemd-run --user --scope bash -c "cd ${WORKSPACE} && . ${VENV_DIR}/bin/activate && python app.py > flask.log 2>&1 &"
                            sleep 3
                        fi
                        
                        # Method 3: Traditional nohup with disown
                        if ! pgrep -f "python.*app.py" > /dev/null; then
                            echo "Using nohup with disown..."
                            bash -c "cd ${WORKSPACE} && . ${VENV_DIR}/bin/activate && nohup python app.py > flask.log 2>&1 & disown" || true
                            sleep 3
                        fi
                        
                        # Final check
                        if pgrep -f "python.*app.py" > /dev/null; then
                            echo "✅ Flask app started with alternative method!"
                        else
                            echo "❌ All methods failed. Check logs:"
                            cat flask.log 2>/dev/null || echo "No log file found"
                            exit 1
                        fi
                    fi
                '''
            }
        }
        stage('Health Check') {
            steps {
                echo "Performing health check..."
                sh '''
                    sleep 5
                    
                    # Check if process is still running
                    if ! pgrep -f "python.*app.py" > /dev/null; then
                        echo "❌ Flask process not found after health check wait"
                        echo "Process list:"
                        ps aux | grep python
                        echo "Flask logs:"
                        tail -20 flask.log 2>/dev/null || echo "No log file"
                        exit 1
                    fi
                    
                    # Test local connectivity with retries
                    for i in {1..5}; do
                        echo "Health check attempt $i/5..."
                        if curl -f -s --max-time 10 http://localhost:${APP_PORT}/ > /dev/null; then
                            echo "✅ Health check passed!"
                            break
                        else
                            echo "⏳ Waiting for app to be ready..."
                            sleep 5
                        fi
                        
                        if [ $i -eq 5 ]; then
                            echo "❌ Health check failed after 5 attempts"
                            echo "Process status:"
                            ps aux | grep "python.*app.py" | grep -v grep || echo "No Flask process"
                            echo "Port status:"
                            sudo netstat -tlnp | grep :${APP_PORT} || echo "Port not listening"
                            echo "Flask logs:"
                            tail -30 flask.log 2>/dev/null || echo "No log file"
                            exit 1
                        fi
                    done
                '''
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
            sh '''
                echo "=== Final Deployment Summary ==="
                echo "Workspace: ${WORKSPACE}"
                echo "App Port: ${APP_PORT}"
                
                echo "Process Status:"
                ps aux | grep "python.*app.py" | grep -v grep || echo "❌ No Flask process found"
                
                echo "Port Status:"
                sudo netstat -tlnp | grep :${APP_PORT} || echo "❌ Port ${APP_PORT} not listening"
                
                if pgrep -f "python.*app.py" > /dev/null; then
                    PRIVATE_IP=$(hostname -I | awk '{print $1}')
                    PUBLIC_IP=$(curl -s --max-time 3 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "Not Available")
                    
                    echo "✅ Flask app is running!"
                    echo "Access URLs:"
                    echo "  Private: http://$PRIVATE_IP:${APP_PORT}"
                    if [ "$PUBLIC_IP" != "Not Available" ]; then
                        echo "  Public: http://$PUBLIC_IP:${APP_PORT} (if security group allows)"
                    fi
                else
                    echo "❌ Flask app is not running"
                fi
            '''
        }
        success {
            echo 'Pipeline succeeded ✅'
        }
        failure {
            echo 'Pipeline failed ❌'
        }
    }
}
