node{
    stage('Checkout'){
        def dockerHome = tool 'docker'
        env.PATH = "${dockerHome}/bin"
        checkout scm
    }

    stage('Build image') {
        withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
            sh "docker login --username=mygituks --password=mdj1646MDJ"
            sh "docker build -t my_git_uks -f Dockerfile ."
            sh "docker tag my_git_uks gituks/uks-git-2019:second"
        }
    }
    stage('Run Tests') {
        withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
            sh "docker exec my_git_uks python manage.py test"
        }

    }
    stage('Push image') {
        withEnv(['PATH+EXTRA=/usr/sbin:/usr/bin:/sbin:/bin']){
            sh "docker push gituks/uks-git-2019:second"
        }
    }
}