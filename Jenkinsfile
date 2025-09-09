pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root'  // run as root inside container
        }
    }

    environment {
        APP_NAME   = 'flask-demo'
        APP_PORT   = '5000'
        DEPLOY_DIR = '/opt/flask-demo'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: "https://github.com/Devakesavan/Jenkins_demo.git", branch: "main", credentialsId: "github-credentials"
            }
        }

        stage('Build') {
            steps {
                sh '''
                  set -eux
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                  set -eux
                  chmod +x test.sh
                  ./test.sh
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                  set -eux
                  echo "Starting app with Gunicorn..."
                  gunicorn -b 0.0.0.0:${APP_PORT} app:app &
                '''
            }
        }
    }
}
