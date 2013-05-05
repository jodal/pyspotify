from fabric.api import execute, local, settings, task


@task
def preprocess_header():
    local('cpp -nostdinc spotify/api.h > spotify/api.processed.h || true')


@task
def test():
    local('nosetests')


@task
def autotest():
    while True:
        local('clear')
        with settings(warn_only=True):
            execute(test)
        local(
            'inotifywait -q -e create -e modify -e delete '
            '--exclude ".*\.(pyc|sw.)" -r spotify/ tests/')
