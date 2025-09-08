pipeline {
    agent any

    environment {
        BRANCH = 'main'
        APP_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                // If repo is private, configure credentialsId
                git branch: "${BRANCH}",
                    url: 'https://github.com/Devakesavan/Jenkins_demo.git',
                    credentialsId: 'github-credentials'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing Python and dependencies..."
                sh '''
                    sudo apt-get update -y
                    sudo apt-get install -y python3 python3-pip

                    if [ -f requirements.txt ]; then
                        pip3 install -r requirements.txt
                    fi
                '''
            }
        }

        stage('Build') {
            steps {
                echo "Running build script..."
                sh 'chmod +x build.sh'
                sh './build.sh'
            }
        }

        stage('Test') {
            steps {
                echo "Running test script..."
                sh 'chmod +x test.sh'
                sh './test.sh'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying Flask app..."
                sh '''
                    # Kill any existing Flask app process
                    pkill -f app.py || true

                    # Run Flask app in background
                    nohup python3 app.py > flask.log 2>&1 &
                '''
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
        }
        success {
            echo 'Pipeline succeeded ✅'
        }
        failure {
            echo 'Pipeline failed ❌'
        }
    }
}
