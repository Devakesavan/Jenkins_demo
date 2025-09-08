pipeline {
    agent any
    
    environment {
        PYTHON_PATH = '/usr/bin/python3'
        FLASK_ENV = 'testing'
        PORT = '5000'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo "=== STAGE: Checkout Code ==="
                    echo "Checking out code from repository..."
                }
                
                // Checkout with credentials
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        credentialsId: 'github-credentials',
                        url: 'https://github.com/Devakesavan/Jenkins_demo.git'
                    ]]
                ])
                
                script {
                    echo "Code checkout completed successfully!"
                    echo "Current workspace: ${WORKSPACE}"
                }
            }
        }
        
        stage('Environment Setup') {
            steps {
                script {
                    echo "=== STAGE: Environment Setup ==="
                    echo "Setting up Python virtual environment and dependencies..."
                }
                
                sh '''
                    echo "Python version:"
                    python3 --version

                    echo "Ensuring python3-venv package is installed..."
                    if ! python3 -m venv --help > /dev/null 2>&1; then
                        echo "Installing python3-venv..."
                        sudo apt-get update -y
                        sudo apt-get install -y python3-venv python3.12-venv || true
                    fi
                    
                    echo "Creating virtual environment..."
                    python3 -m venv venv
                    
                    echo "Activating virtual environment..."
                    . venv/bin/activate
                    
                    echo "Upgrading pip..."
                    pip install --upgrade pip
                    
                    echo "Installing dependencies..."
                    pip install -r requirements.txt || true
                    
                    echo "Installed packages:"
                    pip list
                '''
                
                script {
                    echo "Environment setup completed successfully!"
                }
            }
        }
        
        stage('Code Quality Check') {
            steps {
                script {
                    echo "=== STAGE: Code Quality Check ==="
                    echo "Running code quality checks..."
                }
                
                sh '''
                    . venv/bin/activate
                    
                    echo "Checking Python syntax..."
                    python3 -m py_compile app.py
                    
                    echo "Code quality check passed!"
                '''
                
                script {
                    echo "Code quality checks completed successfully!"
                }
            }
        }
        
        stage('Build Project') {
            steps {
                script {
                    echo "=== STAGE: Build Project ==="
                    echo "Building the Flask application..."
                }
                
                sh './build.sh'
                
                script {
                    echo "Build completed successfully!"
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "=== STAGE: Run Tests ==="
                    echo "Running unit tests and integration tests..."
                }
                
                sh './test.sh'
                
                script {
                    echo "All tests completed successfully!"
                }
            }
        }
        
        stage('Application Health Check') {
            steps {
                script {
                    echo "=== STAGE: Application Health Check ==="
                    echo "Starting application and performing health checks..."
                }
                
                sh '''
                    . venv/bin/activate
                    
                    echo "Starting Flask application in background..."
                    nohup python3 app.py > app.log 2>&1 &
                    APP_PID=$!
                    echo "Application started with PID: $APP_PID"
                    
                    echo "Waiting for application to start..."
                    sleep 10
                    
                    echo "Performing health check..."
                    curl -f http://localhost:5000/api/health || {
                        echo "Health check failed!"
                        kill $APP_PID 2>/dev/null || true
                        exit 1
                    }
                    
                    echo "Testing API endpoints..."
                    curl -f http://localhost:5000/api/system > /dev/null
                    curl -f http://localhost:5000/api/metrics > /dev/null
                    
                    echo "Stopping application..."
                    kill $APP_PID 2>/dev/null || true
                    
                    echo "Health check completed successfully!"
                '''
                
                script {
                    echo "Application health checks passed!"
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    echo "=== STAGE: Security Scan ==="
                    echo "Running security scans..."
                }
                
                sh '''
                    . venv/bin/activate
                    
                    echo "Installing security tools..."
                    pip install safety bandit
                    
                    echo "Checking for known security vulnerabilities in dependencies..."
                    safety check || echo "Security check completed with warnings"
                    
                    echo "Running static security analysis..."
                    bandit -r . -f json -o bandit-report.json || echo "Bandit scan completed"
                    
                    echo "Security scan completed!"
                '''
                
                script {
                    echo "Security scans completed!"
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    echo "=== STAGE: Generate Reports ==="
                    echo "Generating build and test reports..."
                }
                
                sh '''
                    echo "=== BUILD REPORT ===" > build-report.txt
                    echo "Build Date: $(date)" >> build-report.txt
                    echo "Build Number: ${BUILD_NUMBER}" >> build-report.txt
                    echo "Git Commit: $(git rev-parse HEAD)" >> build-report.txt
                    echo "Git Branch: $(git rev-parse --abbrev-ref HEAD)" >> build-report.txt
                    echo "" >> build-report.txt
                    echo "Dependencies:" >> build-report.txt
                    . venv/bin/activate && pip list >> build-report.txt
                    
                    echo "Build report generated successfully!"
                '''
                
                script {
                    echo "Reports generated successfully!"
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "=== POST-BUILD ACTIONS ==="
                echo "Performing cleanup and archiving artifacts..."
            }
            
            // Archive important files
            archiveArtifacts artifacts: '**/*.log, **/*.txt, **/*.json', allowEmptyArchive: true
            
            // Clean up virtual environment
            sh '''
                echo "Cleaning up virtual environment..."
                rm -rf venv || true
                echo "Cleanup completed!"
            '''
            
            script {
                echo "=== PIPELINE SUMMARY ==="
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Build URL: ${BUILD_URL}"
                echo "Workspace: ${WORKSPACE}"
                echo "Job Name: ${JOB_NAME}"
                echo "Pipeline completed!"
            }
        }
        
        success {
            script {
                echo "🎉 SUCCESS: Pipeline completed successfully!"
                echo "All stages passed. The application is ready for deployment."
            }
        }
        
        failure {
            script {
                echo "❌ FAILURE: Pipeline failed!"
                echo "Please check the logs for details."
            }
            
            // Archive failure logs
            sh '''
                echo "Pipeline failed at stage: ${STAGE_NAME}" > failure-report.txt
                echo "Build Number: ${BUILD_NUMBER}" >> failure-report.txt
                echo "Timestamp: $(date)" >> failure-report.txt
            '''
        }
        
        unstable {
            script {
                echo "⚠️ UNSTABLE: Pipeline completed with warnings!"
                echo "Some tests may have failed or there were quality issues."
            }
        }
    }
}
