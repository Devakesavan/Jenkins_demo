pipeline {
    agent {
        docker {
            image 'python:3.12-slim'   // Preinstalled Python + venv
            args '-u root'             // Run as root to allow installs if needed
        }
    }
    
    environment {
        PYTHON_PATH = '/usr/local/bin/python3'
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
                sh '''
                    echo "=== STAGE: Environment Setup ==="
                    echo "Python version:"
                    python3 --version
                    
                    echo "Creating virtual environment..."
                    python3 -m venv venv
                    
                    echo "Activating virtual environment..."
                    . venv/bin/activate
                    
                    echo "Upgrading pip..."
                    pip install --upgrade pip
                    
                    echo "Installing dependencies..."
                    pip install -r requirements.txt
                    
                    echo "Installed packages:"
                    pip list
                '''
            }
        }
        
        stage('Code Quality Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo "Checking Python syntax..."
                    python3 -m py_compile app.py
                    echo "Code quality check passed!"
                '''
            }
        }
        
        stage('Build Project') {
            steps {
                sh '''
                    echo "=== STAGE: Build Project ==="
                    ./build.sh
                    echo "Build completed successfully!"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    echo "=== STAGE: Run Tests ==="
                    ./test.sh
                    echo "All tests completed successfully!"
                '''
            }
        }
        
        stage('Application Health Check') {
            steps {
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
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo "Installing security tools..."
                    pip install safety bandit
                    
                    echo "Checking for known vulnerabilities..."
                    safety check || echo "Security check completed with warnings"
                    
                    echo "Running static security analysis..."
                    bandit -r . -f json -o bandit-report.json || echo "Bandit scan completed"
                '''
            }
        }
        
        stage('Generate Reports') {
            steps {
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
            }
        }
    }
    
    post {
        always {
            echo "=== POST-BUILD ACTIONS ==="
            echo "Performing cleanup and archiving artifacts..."
            
            archiveArtifacts artifacts: '**/*.log, **/*.txt, **/*.json', allowEmptyArchive: true
            
            sh '''
                echo "Cleaning up virtual environment..."
                rm -rf venv || true
                echo "Cleanup completed!"
            '''
            
            echo "=== PIPELINE SUMMARY ==="
            echo "Build Number: ${BUILD_NUMBER}"
            echo "Build URL: ${BUILD_URL}"
            echo "Workspace: ${WORKSPACE}"
            echo "Job Name: ${JOB_NAME}"
            echo "Pipeline completed!"
        }
        
        success {
            echo "🎉 SUCCESS: Pipeline completed successfully!"
        }
        
        failure {
            echo "❌ FAILURE: Pipeline failed!"
            sh '''
                echo "Pipeline failed at stage: ${STAGE_NAME}" > failure-report.txt
                echo "Build Number: ${BUILD_NUMBER}" >> failure-report.txt
                echo "Timestamp: $(date)" >> failure-report.txt
            '''
        }
        
        unstable {
            echo "⚠️ UNSTABLE: Pipeline completed with warnings!"
        }
    }
}
