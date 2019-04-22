node ('docker'){

    /*stage 'Initialize'
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin:${env.PATH}"*/

    stage 'Clone repository'
        checkout scm

    stage 'Build image'
        sh "docker build -f Dockerfile ."

}