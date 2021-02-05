node('docker') {
    stage('Checkout'){
        checkout scm
        execute("git submodule update --init --recursive")
    }
    stage('Print Environmental Variables'){
        environVars()
    }
    stage('Setup Python'){
        execute("python -m pip install cogapp")
        execute("python -m pip install setuptools wheel")
    }
    stage('Create Wheel'){
        execute("python setup.py bdist_wheel")
    }
    stage('Install Kojen locally from this repository'){
        execute("python -m pip install --no-index ./dist/*.whl")
    }
    stage('Generate example code'){
        execute("python example/generate.py")
    }
    stage('Clean local Kojen'){
        execute("python -m pip uninstall kojen -y")
    }
    stage('Create Build Environment'){
        execute("cmake -E make_directory ${env.WORKSPACE}/build")
    }
    stage('Configure CMake'){
        execute("cmake -S ${env.WORKSPACE}/example/autogen/allplatforms -B ${env.WORKSPACE}/build -DCMAKE_BUILD_TYPE=${env.BUILD_TYPE}")
    }
    stage('Build'){
        execute("cmake --build ${env.WORKSPACE}/build --config ${env.BUILD_TYPE}")
    }
    stage('Run Tests'){
        execute("${env.WORKSPACE}/build/${env.BUILD_TYPE}/RunTests")
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
        sh(commandString)
    } else {
        bat(commandString)
    }
}

/**
 * Execute a program that exists in the current working directory.
 *
 * On Unix, the current working directory is not implicitly in the PATH,
 * so the command must be prefixed with "./".
 *
 * On Windows, the current directory is first in the search path, but
 * it does not like the "./" used for a Unix-style command.
 *
 * Therefore we have to do something special in each case.
 */
def executeCwd(commandString) {
    if (isUnix()) {
        execute("./" + commandString)
    } else {
        execute(".\\" + commandString)
    }
}