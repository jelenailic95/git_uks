node{
    stage('Checkout'){
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin"
        checkout scm
    }

    stage('Build and push image') {
        withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
            sh "docker login --username=mygituks --password=mdj1646MDJ"
            sh "docker build -t my_git_uks -f Dockerfile ."
            sh "docker tag my_git_uks gituks2019/git_uks:first"
            sh "docker push gituks2019/git_uks:first"
        }
    }
}