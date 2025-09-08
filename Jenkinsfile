pipeline {
    agent any
    
    environment {
        // Environment variables for the pipeline
        PYTHON_PATH = '/usr/bin/python3'
        FLASK_ENV = 'development'
        APP_PORT = '5000'
        
        // Notification settings
        NOTIFICATION_EMAIL = 'your-email@example.com'
    }
    
    options {
        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        
        // Timeout for the entire pipeline
        timeout(time: 20, unit: 'MINUTES')
        
        // Timestamps in console output
        timestamps()
        
        // Disable concurrent builds
        disableConcurrentBuilds()
    }
    
    triggers {
        // Poll SCM every 2 minutes for changes
        pollSCM('H/2 * * * *')
        
        // Optional: Trigger build daily at 2 AM
        cron('0 2 * * *')
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                echo '🔄 Starting checkout process...'
                
                // Clean workspace before checkout
                cleanWs()
                
                // Checkout code from SCM
                checkout scm
                
                echo '✅ Code checkout completed'
                
                script {
                    // Get git information
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    
                    env.GIT_BRANCH_NAME = sh(
                        script: 'git branch --show-current || git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()
                    
                    env.BUILD_TIMESTAMP = sh(
                        script: 'date "+%Y-%m-%d %H:%M:%S"',
                        returnStdout: true
                    ).trim()
                }
                
                // Display build information
                echo "📋 Build Information:"
                echo "  📅 Build Time: ${env.BUILD_TIMESTAMP}"
                echo "  🌿 Git Branch: ${env.GIT_BRANCH_NAME}"
                echo "  📝 Git Commit: ${env.GIT_COMMIT_SHORT}"
                echo "  🏗️  Build Number: ${env.BUILD_NUMBER}"
                echo "  💼 Workspace: ${env.WORKSPACE}"
            }
        }
        
        stage('Environment Setup') {
            steps {
                echo '⚙️ Setting up environment...'
                
                script {
                    // Check Python version
                    def pythonVersion = sh(
                        script: 'python3 --version',
                        returnStdout: true
                    ).trim()
                    echo "🐍 Python Version: ${pythonVersion}"
                    
                    // Check if required files exist
                    if (!fileExists('app.py')) {
                        error('❌ app.py not found in repository')
                    }
                    
                    if (!fileExists('build.sh')) {
                        error('❌ build.sh not found in repository')
                    }
                    
                    if (!fileExists('test.sh')) {
                        error('❌ test.sh not found in repository')
                    }
                    
                    echo '✅ All required files are present'
                    
                    // Make scripts executable
                    sh 'chmod +x build.sh test.sh'
                    echo '✅ Scripts made executable'
                }
            }
        }
        
        stage('Build Project') {
            steps {
                echo '🔨 Starting build process...'
                
                script {
                    try {
                        // Run the build script
                        sh './build.sh'
                        echo '✅ Build completed successfully'
                        
                        // Verify build artifacts
                        if (fileExists('build_info.txt')) {
                            echo '📊 Build Information:'
                            sh 'cat build_info.txt'
                        }
                        
                    } catch (Exception e) {
                        echo "❌ Build failed: ${e.getMessage()}"
                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
            
            post {
                always {
                    // Archive build logs
                    archiveArtifacts artifacts: 'logs/**/*.log', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'build_info.txt', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'artifacts/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Starting test process...'
                
                script {
                    try {
                        // Run the test script
                        sh './test.sh'
                        echo '✅ All tests completed successfully'
                        
                    } catch (Exception e) {
                        echo "❌ Tests failed: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                        throw e
                    }
                }
            }
            
            post {
                always {
                    // Archive test results
                    archiveArtifacts artifacts: 'test_reports/**/*', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'logs/**/*.log', allowEmptyArchive: true
                    
                    // Publish JUnit test results if available
                    script {
                        if (fileExists('test_reports/junit.xml')) {
                            publishTestResults testResultsPattern: 'test_reports/junit.xml'
                            echo '📊 Test results published'
                        }
                    }
                }
                
                success {
                    echo '✅ All tests passed successfully'
                }
                
                failure {
                    echo '❌ Some tests failed'
                }
                
                unstable {
                    echo '⚠️ Tests completed with warnings'
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🔒 Running security checks...'
                
                script {
                    try {
                        // Basic security checks
                        sh '''
                            echo "🔍 Checking for sensitive files..."
                            
                            # Check for common sensitive files
                            if find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "id_rsa*" | grep -q .; then
                                echo "⚠️ Warning: Sensitive files detected"
                            else
                                echo "✅ No sensitive files detected"
                            fi
                            
                            # Check for hardcoded secrets in Python files
                            echo "🔍 Scanning for potential secrets..."
                            if grep -r -i "password\\|secret\\|api_key\\|token" *.py | grep -v "# nosec" | grep -q "="; then
                                echo "⚠️ Warning: Potential secrets found in code"
                                grep -r -i "password\\|secret\\|api_key\\|token" *.py | grep -v "# nosec" | head -5
                            else
                                echo "✅ No obvious secrets found in code"
                            fi
                            
                            # Check dependencies for known vulnerabilities (basic check)
                            echo "🔍 Checking Python dependencies..."
                            if command -v safety >/dev/null 2>&1; then
                                safety check
                            else
                                echo "⚠️ Safety scanner not available, skipping vulnerability check"
                            fi
                            
                            echo "✅ Security scan completed"
