pipeline {
    agent any
    
    environment {
        // Set FAIL_TEST to 'true' to simulate test failure
        FAIL_TEST = 'false'
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/your-repo.git'
                echo 'Code checkout completed'
            }
        }
        
        stage('Build Project') {
            steps {
                sh 'chmod +x build.sh'
                sh './build.sh'
            }
            
            post {
                success {
                    echo 'Build stage completed successfully'
                }
                failure {
                    echo 'Build stage failed'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'chmod +x test.sh'
                sh './test.sh'
            }
            
            post {
                success {
                    echo 'Test stage completed successfully'
                }
                failure {
                    echo 'Test stage failed'
                    // Uncomment the next line to fail the build on test failure
                    // error('Tests failed')
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'build/**/*'
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
