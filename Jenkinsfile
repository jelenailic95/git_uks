node{
    stage('Checkout'){
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin"
        checkout scm
    }

    stage('Build image and push image') {
        withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
            sh "docker build -f Dockerfile ."
            sh "docker push gituks2019/git_uks:first"
        }
    }
}