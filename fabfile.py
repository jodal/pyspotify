from fabric.api import execute, local, settings, task


@task
def preprocess_header():
    local('cpp -nostdinc spotify/api.h > spotify/api.processed.h || true')


@task
def docs():
    local('make -C docs/ html')


@task
def autodocs():
    auto(docs)


@task
def test():
    local('nosetests')


@task
def autotest():
    auto(test)


@task
def coverage():
    local('nosetests --with-coverage --cover-package=spotify --cover-branches')


@task
def autocoverage():
    auto(coverage)


def auto(task):
    while True:
        local('clear')
        with settings(warn_only=True):
            execute(task)
        local(
            'inotifywait -q -e create -e modify -e delete '
            '--exclude ".*\.(pyc|sw.)" -r docs/ spotify/ tests/')


@task
def update_authors():
    # Keep authors in the order of appearance and use awk to filter out dupes
    local(
        "git log --format='- %aN <%aE>' --reverse | awk '!x[$0]++' > AUTHORS")
