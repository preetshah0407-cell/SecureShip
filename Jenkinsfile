
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'secureship-demo'
        CONTAINER_NAME = 'secureship-demo-ci'
        VENV = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source checked out from GitHub'
                sh 'pwd && git log -1 --oneline'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv ${VENV}
                    ${VENV}/bin/pip install -r requirements.txt pytest
                '''
            }
        }

        stage('Automated Tests') {
            steps {
                sh 'PYTHONPATH=. ${VENV}/bin/pytest -v'
            }
        }

        stage('SonarQube Code Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        SCANNER_HOME=/var/lib/jenkins/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner
                        "$SCANNER_HOME/bin/sonar-scanner" \
                          -Dsonar.projectKey=secureship \
                          -Dsonar.projectName=SecureShip \
                          -Dsonar.sources=app.py \
                          -Dsonar.tests=tests \
                          -Dsonar.python.version=3.12
                    '''
                }
            }
        }

        stage('Source Security Scan') {
            steps {
                sh 'trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL .'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }

        stage('Container Vulnerability Scan') {
            steps {
                sh 'trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 ${IMAGE_NAME}:${BUILD_NUMBER}'
            }
        }

        stage('Deploy and Health Check') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true
                    docker run -d --name ${CONTAINER_NAME} -p 5001:5000 ${IMAGE_NAME}:${BUILD_NUMBER}
                    sleep 5
                    curl --fail http://localhost:5001/health
                '''
            }
        }
    }

    post {
        success {
            echo 'SecureShip pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Review the failed stage and its console output.'
        }
    }
}

