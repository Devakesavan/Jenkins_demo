pipeline {
    agent any

    environment {
        BRANCH = 'main'
        APP_PORT = '5000'
        VENV_DIR = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${BRANCH}",
                    url: 'https://github.com/Devakesavan/Jenkins_demo.git',
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
            when {
                branch 'main'
            }
            steps {
                echo "Deploying Flask app..."
                sh '''
                    # Kill any existing Flask app process
                    pkill -f app.py || true

                    # Run Flask app in background using venv Python
                    . ${VENV_DIR}/bin/activate
                    nohup python app.py > flask.log 2>&1 &
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
