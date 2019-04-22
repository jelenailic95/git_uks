pipeline {
    agent {
        dockerfile true
    }
    stages {
        stage('Clone repository'){
            checkout scm
        }
        stage('Build image'){
            steps {
                sh "docker build -f Dockerfile ."
            }
        }
    }

}