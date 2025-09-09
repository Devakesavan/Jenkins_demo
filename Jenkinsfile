pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root'
        }
    }

    environment {
        APP_NAME   = 'flask-demo'
        APP_PORT   = '5000'
        DEPLOY_DIR = '/opt/flask-demo'
        DEPLOY_SERVER = 'your-server-ip'
        DEPLOY_USER = 'deploy-user'
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
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                  # Install pytest first
                  pip install pytest
                  chmod +x test.sh
                  ./test.sh
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Copy files to deployment server
                    sh "rsync -avz --delete -e ssh . ${DEPLOY_USER}@${DEPLOY_SERVER}:${DEPLOY_DIR}/"
                    
                    // Restart application on deployment server
                    sshagent(['your-ssh-credentials']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_SERVER} '
                                cd ${DEPLOY_DIR}
                                pip install -r requirements.txt
                                pkill -f gunicorn || true
                                nohup gunicorn -b 0.0.0.0:${APP_PORT} app:app > app.log 2>&1 &
                            '
                        """
                    }
                }
            }
        }
    }
}
