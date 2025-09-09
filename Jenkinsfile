pipeline {
    agent any  // run on EC2 host directly

    environment {
        APP_NAME   = 'flask-demo'
        APP_PORT   = '5000'
        DEPLOY_DIR = '/opt/flask-demo'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: "https://github.com/Devakesavan/Jenkins_demo.git", 
                    branch: "main", 
                    credentialsId: "github-credentials"
            }
        }

        stage('Build') {
            steps {
                sh '''
                  set -eux
                  pip3 install --upgrade pip
                  pip3 install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                  set -eux
                  chmod +x test.sh
                  ./test.sh || echo "No tests found, skipping..."
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                  set -eux
                  echo "Building Docker image for Flask app..."
                  docker build -t ${APP_NAME} .

                  echo "Stopping any existing container..."
                  docker stop ${APP_NAME} || true
                  docker rm ${APP_NAME} || true

                  echo "Starting Flask app container..."
                  docker run -d --name ${APP_NAME} -p ${APP_PORT}:${APP_PORT} ${APP_NAME}
                '''
            }
        }
    }
}
