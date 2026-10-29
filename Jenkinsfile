
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
                    set -eu

                    PREVIOUS_IMAGE=$(docker inspect \
                        --format='{{.Config.Image}}' \
                        ${CONTAINER_NAME} 2>/dev/null || true)

                    PREVIOUS_RUNNING=$(docker inspect \
                        --format='{{.State.Running}}' \
                        ${CONTAINER_NAME} 2>/dev/null || true)

                    docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true

                    rollback() {
                        echo "Deployment failed. Rolling back..."

                        docker rm -f ${CONTAINER_NAME} >/dev/null 2>&1 || true

                        if [ -n "$PREVIOUS_IMAGE" ] && \
                           [ "$PREVIOUS_RUNNING" = "true" ]; then
                            docker run -d \
                                --name ${CONTAINER_NAME} \
                                -p 5001:5000 \
                                "$PREVIOUS_IMAGE"

                            sleep 5

                            if curl --fail --silent \
                                http://localhost:5001/health >/dev/null; then
                                echo "Rollback successful."
                            else
                                echo "WARNING: Rollback health check failed."
                            fi
                        else
                            echo "No previously running container available."
                        fi
                    }

                    if ! docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5001:5000 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}; then
                        rollback
                        exit 1
                    fi

                    sleep 5

                    if ! curl --fail --silent \
                        http://localhost:5001/health; then
                        rollback
                        exit 1
                    fi

                    echo "Deployment and health check successful."
                '''
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

