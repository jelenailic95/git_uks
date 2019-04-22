node{
    stage('Initialize') {
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin"
    }
    stage('Checkout'){
        checkout scm
    }

    stage('Build image') {
        sh "docker build -f Dockerfile ."
    }
}