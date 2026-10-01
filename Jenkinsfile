pipeline {
    agent any

    environment {
        APP_DIR = 'backend/4-api'
        IMAGE_NAME = 'actividades-api'
        REGISTRY = 'docker.io'
    }

    parameters {
        string(name: 'DOCKERHUB_NAMESPACE', defaultValue: 'replace-with-dockerhub-user', description: 'Usuario o namespace de Docker Hub; no es un secreto.')
    }

    options {
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
        timeout(time: 20, unit: 'MINUTES')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Lint and tests') {
            steps {
                dir(env.APP_DIR) {
                    sh 'python3 -m venv .ci-venv'
                    sh '.ci-venv/bin/pip install --upgrade pip'
                    sh '.ci-venv/bin/pip install -r requirements-dev.txt'
                    withEnv([
                        'SECRET_KEY=jenkins-ci-only-secret',
                        'DEBUG=False',
                        'ALLOWED_HOSTS=localhost,127.0.0.1',
                        'DB_NAME=actividades',
                        'DB_USER=actividades',
                        'DB_PASSWORD=jenkins-ci-password',
                        'DB_HOST=127.0.0.1',
                        'DB_PORT=5432'
                    ]) {
                        sh '.ci-venv/bin/ruff check .'
                        sh '.ci-venv/bin/python manage.py check'
                        sh '.ci-venv/bin/pytest --cov=apps --cov-fail-under=80'
                    }
                }
            }
        }

        stage('Build image') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                }
            }
            steps {
                script {
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(12)}"
                    sh "docker build --pull -t ${REGISTRY}/${DOCKERHUB_NAMESPACE}/${IMAGE_NAME}:${env.IMAGE_TAG} ${APP_DIR}"
                }
            }
        }

        stage('Scan image') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                }
            }
            steps {
                sh "trivy image --exit-code 1 --ignore-unfixed --severity HIGH,CRITICAL ${REGISTRY}/${DOCKERHUB_NAMESPACE}/${IMAGE_NAME}:${env.IMAGE_TAG}"
            }
        }

        stage('Publish image') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                }
            }
            steps {
                script {
                    docker.withRegistry("https://${REGISTRY}", 'dockerhub-creds') {
                        def image = docker.image("${REGISTRY}/${DOCKERHUB_NAMESPACE}/${IMAGE_NAME}:${env.IMAGE_TAG}")
                        image.push()
                        if (env.BRANCH_NAME == 'main') {
                            image.push('latest')
                        }
                        if (env.TAG_NAME) {
                            image.push(env.TAG_NAME)
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            dir(env.APP_DIR) { sh 'rm -rf .ci-venv' }
        }
        success { echo "Pipeline exitoso: ${REGISTRY}/${DOCKERHUB_NAMESPACE}/${IMAGE_NAME}:${env.IMAGE_TAG ?: 'no publicado'}" }
        failure { echo 'Build fallido. Revisar los logs del stage correspondiente.' }
    }
}
