pipeline {
    agent any
    environment {
        APP_PORT = '5000'
        VENV_DIR = '.venv'
        FLASK_HOST = '0.0.0.0'
        SERVICE_NAME = 'flask-app'
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
                    echo "Stopping existing Flask processes..."
                    pkill -f "python.*app.py" || true
                    sleep 2
                    
                    echo "Creating systemd service file..."
                    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Flask DevOps Application
After=network.target

[Service]
Type=simple
User=jenkins
WorkingDirectory=${WORKSPACE}
Environment=PATH=${WORKSPACE}/${VENV_DIR}/bin
Environment=PORT=${APP_PORT}
Environment=FLASK_ENV=production
Environment=FLASK_HOST=${FLASK_HOST}
ExecStart=${WORKSPACE}/${VENV_DIR}/bin/python app.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

                    echo "Reloading systemd and starting service..."
                    sudo systemctl daemon-reload
                    sudo systemctl stop ${SERVICE_NAME} || true
                    sudo systemctl start ${SERVICE_NAME}
                    sudo systemctl enable ${SERVICE_NAME}
                    
                    echo "Waiting for service to start..."
                    sleep 10
                    
                    # Check service status
                    if sudo systemctl is-active ${SERVICE_NAME} >/dev/null; then
                        echo "✅ Flask service started successfully!"
                        sudo systemctl status ${SERVICE_NAME} --no-pager
                    else
                        echo "❌ Flask service failed to start!"
                        sudo systemctl status ${SERVICE_NAME} --no-pager
                        sudo journalctl -u ${SERVICE_NAME} --no-pager -n 20
                        exit 1
                    fi
                '''
            }
        }
        stage('Health Check') {
            steps {
                echo "Performing health check..."
                sh '''
                    echo "Checking service status..."
                    sudo systemctl status ${SERVICE_NAME} --no-pager
                    
                    echo "Testing connectivity..."
                    for i in {1..10}; do
                        echo "Health check attempt $i/10..."
                        if curl -f -s --max-time 5 http://localhost:${APP_PORT}/ > /dev/null; then
                            echo "✅ Health check passed!"
                            
                            # Get IP addresses
                            PRIVATE_IP=$(hostname -I | awk '{print $1}')
                            PUBLIC_IP=$(curl -s --max-time 3 http://checkip.amazonaws.com 2>/dev/null || echo "Unknown")
                            
                            echo "🌐 Application is accessible at:"
                            echo "  Local: http://localhost:${APP_PORT}"
                            echo "  Private: http://$PRIVATE_IP:${APP_PORT}"
                            echo "  Public: http://$PUBLIC_IP:${APP_PORT}"
                            echo ""
                            echo "⚠️  Make sure EC2 Security Group allows inbound traffic on port ${APP_PORT}"
                            break
                        else
                            echo "⏳ Waiting for app to be ready..."
                            sleep 3
                        fi
                        
                        if [ $i -eq 10 ]; then
                            echo "❌ Health check failed after 10 attempts"
                            echo "Service logs:"
                            sudo journalctl -u ${SERVICE_NAME} --no-pager -n 30
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
                
                if sudo systemctl is-active ${SERVICE_NAME} >/dev/null; then
                    echo "✅ Flask service is running"
                    PRIVATE_IP=$(hostname -I | awk '{print $1}')
                    PUBLIC_IP=$(curl -s --max-time 3 http://checkip.amazonaws.com 2>/dev/null || echo "Unknown")
                    
                    echo "🌐 Access your application:"
                    echo "  Public URL: http://$PUBLIC_IP:${APP_PORT}"
                    echo "  Private URL: http://$PRIVATE_IP:${APP_PORT}"
                    echo ""
                    echo "📋 Service management commands:"
                    echo "  Status: sudo systemctl status ${SERVICE_NAME}"
                    echo "  Logs: sudo journalctl -u ${SERVICE_NAME} -f"
                    echo "  Restart: sudo systemctl restart ${SERVICE_NAME}"
                else
                    echo "❌ Flask service is not running"
                    sudo systemctl status ${SERVICE_NAME} --no-pager || true
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
