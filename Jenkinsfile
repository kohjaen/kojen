#!groovy
// Adapted from 'Controlling cell behavior at runtime' here : https://www.jenkins.io/blog/2019/11/22/welcome-to-the-matrix/
pipeline {
    // Note : with a parameter choice, the first choice is the default.
    parameters {
        choice(name: 'PLATFORM_FILTER', choices: ['all', 'centos7', 'centos8','ubuntu20'], description: 'Run on a specific build platform')
        choice(name: 'BUILD_TYPE', choices: ['Release', 'Debug'], description: 'Desired build configuration')
    }
    options { 
        disableConcurrentBuilds() 
        // Only keep the 3 most recent builds
        buildDiscarder(logRotator(numToKeepStr:'3'))
    } 
    agent none
    stages {
        stage('BuildAndTest') {
            matrix {
                agent {
                    docker{
                        image "${PLATFORM}-slave"
                    }
                }
                when { anyOf {
                    expression { params.PLATFORM_FILTER == 'all' }
                    expression { params.PLATFORM_FILTER == env.PLATFORM }
                } }
                axes {
                    axis {
                        name 'PLATFORM'
                        values 'centos7', 'centos8','ubuntu20'
                    }
                    //axis {
                    //    name 'BROWSER'
                    //    values 'firefox', 'chrome', 'safari', 'edge'
                    //}
                }
                stages {
                    stage('Print Environmental Variables'){
                        steps {
                            environVars()
                        }
                    }
                    stage('Checkout'){
                        steps {
                            //checkout([$class: 'GitSCM', branches: [[name: '*/master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[url: 'https://github.com/kohjaen/kojen.git']]])
                            //git branch: 'master', url: 'https://github.com/kohjaen/kojen.git'
							checkout scm
                            execute("git submodule update --init --recursive")
                        }
                    }
                    stage('Setup Python'){
                        steps {
	                        // For some reason, activating a python virtual environment from a bash script does not work (in Centos7 and ubuntu20).
                            //execute("python -m venv ci_venv")
                            //execute("#!/bin/bash")
                            //execute("source ${env.WORKSPACE}/ci_venv/bin/activate")
                            execute("python -m pip install cogapp setuptools wheel")
                            //execute("python -m pip install setuptools wheel")
                        }
                    }
                    stage('Create Wheel'){
                        steps {
                            execute("python setup.py bdist_wheel")
                        }
                    }
                    stage('Install Kojen locally from this repository'){
                        steps {
                            execute("python -m pip install --no-index ./dist/*.whl")
                        }
                    }
                    stage('Generate example code'){
                        steps {
                            execute("python example/generate.py")
                        }
                    }
                    stage('Clean local Kojen'){
                        steps {
                            execute("python -m pip uninstall -y kojen cogapp setuptools wheel")
	                        //execute("deactivate")
	                        //execute("rm -r ci_venv/")
                        }
                    }
                    stage('Create Build Environment'){
                        steps {
                            execute("cmake -E make_directory ${env.WORKSPACE}/build")
                        }
                    }
                    stage('Configure CMake'){
                        steps {
                            execute("cmake -S ${env.WORKSPACE}/example/autogen/allplatforms -B ${env.WORKSPACE}/build -DCMAKE_BUILD_TYPE=${params.BUILD_TYPE}")
                        }
                    }
                    stage('Build'){
                        steps {
                            execute("cmake --build ${env.WORKSPACE}/build --config ${params.BUILD_TYPE}")
                        }
                    }
                    stage('Run Tests'){
                        steps {
                            execute("${env.WORKSPACE}/build/${params.BUILD_TYPE}/RunTests")
                        }
                    }
                }
                post {
                    always {
                        echo "(post::always) I AM ALWAYS first"
                    }
                    changed {
                        echo "(post::changed) CHANGED is run second"
                    }
                    aborted {
                        echo "(post::aborted) SUCCESS, FAILURE, UNSTABLE, or ABORTED are exclusive of each other"
                        deleteDir()
                    }
                    success {
                        echo "(post::success) SUCCESS, FAILURE, UNSTABLE, or ABORTED runs last"
                        deleteDir()
                    }
                    unstable {
                        echo "(post::unstable) SUCCESS, FAILURE, UNSTABLE, or ABORTED runs last"
                        deleteDir()
                    }
                    failure {
                        echo "(post::failure) SUCCESS, FAILURE, UNSTABLE, or ABORTED runs last"
                        deleteDir()
                    }
                }
            }
        }
    }
}

def environVars(){
    if (isUnix()) {
        sh('printenv | sort')
    } else {
        bat('set')
    }
}
def execute(commandString) {
    if (isUnix()) {
        sh(commandString) //-> force bash
        //sh('bash -c "' + commandString + '"')
    } else {
        bat(commandString)
    }
}