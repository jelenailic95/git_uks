node{
    stage('Initialize') {
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin"
    }
    stage('Checkout'){
        checkout scm
    }

    stage('Build image') {
        steps {
            withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
                sh "docker build -f Dockerfile ."
            }
        }
    }
}