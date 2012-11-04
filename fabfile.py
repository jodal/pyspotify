from fabric.api import local


build_dir = 'build/lib/'


def clean():
    local('rm -rf build/')


def build():
    clean()
    local('python setup.py build --with-mock --build-lib {build_dir}'.format(
        build_dir=build_dir))


def test():
    build()
    local('PYTHONPATH={build_dir} nosetests'.format(build_dir=build_dir))


def autotest():
    while True:
        local('clear')
        test()
        local(
            'inotifywait -q -e create -e modify -e delete '
            '--exclude ".*\.(pyc|sw.)" -r spotify/ src/ tests/')
