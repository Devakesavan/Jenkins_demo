pipeline {
    agent any   // run directly on EC2 host (not inside Docker)

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
                  python3 -m venv .venv
                  . .venv/bin/activate
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
                  echo "Deploying app to ${DEPLOY_DIR}..."

                  # Create deploy dir if not exists
                  sudo mkdir -p ${DEPLOY_DIR}
                  sudo cp -r * ${DEPLOY_DIR}

                  cd ${DEPLOY_DIR}

                  # Kill any running Gunicorn for this app
                  if pgrep -f "gunicorn.*${APP_NAME}" > /dev/null; then
                      echo "Stopping existing app..."
                      pkill -f "gunicorn.*${APP_NAME}" || true
                  fi

                  # Start Gunicorn in background
                  echo "Starting app on port ${APP_PORT}..."
                  nohup .venv/bin/gunicorn -b 0.0.0.0:${APP_PORT} app:app \
                    --name ${APP_NAME} > flask.log 2>&1 &
                '''
            }
        }
    }
}
