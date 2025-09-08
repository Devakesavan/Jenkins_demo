pipeline {
    agent any

    environment {
        APP_NAME   = 'flask-demo'
        APP_PORT   = '5000'
        DEPLOY_DIR = '/opt/flask-demo'
        GIT_URL    = 'https://github.com/Devakesavan/Jenkins_demo.git'
        GIT_BRANCH = 'main'
        GIT_CREDS  = 'github-credentials'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: "${GIT_URL}", branch: "${GIT_BRANCH}", credentialsId: "${GIT_CREDS}"
            }
        }

        stage('Build') {
            steps {
                sh '''
                  chmod +x build.sh
                  ./build.sh
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                  chmod +x test.sh
                  ./test.sh
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                  APP_NAME=${APP_NAME}
                  DEPLOY_DIR=${DEPLOY_DIR}

                  # Copy project to deploy directory
                  sudo mkdir -p $DEPLOY_DIR
                  sudo rsync -a --delete ./ $DEPLOY_DIR/
                  sudo chown -R jenkins:jenkins $DEPLOY_DIR

                  # Setup venv in deploy dir
                  if [ ! -d "$DEPLOY_DIR/venv" ]; then
                      python3 -m venv $DEPLOY_DIR/venv
                  fi

                  . $DEPLOY_DIR/venv/bin/activate
                  pip install --upgrade pip
                  pip install -r $DEPLOY_DIR/requirements.txt

                  # Create systemd service for gunicorn
                  sudo tee /etc/systemd/system/${APP_NAME}.service > /dev/null <<EOF
[Unit]
Description=${APP_NAME} via Gunicorn
After=network.target

[Service]
User=jenkins
WorkingDirectory=${DEPLOY_DIR}
Environment="PATH=${DEPLOY_DIR}/venv/bin"
ExecStart=${DEPLOY_DIR}/venv/bin/gunicorn -b 0.0.0.0:${APP_PORT} app:app

[Install]
WantedBy=multi-user.target
EOF

                  # Restart service
                  sudo systemctl daemon-reload
                  sudo systemctl enable ${APP_NAME}
                  sudo systemctl restart ${APP_NAME}
                '''
            }
        }
    }
}
