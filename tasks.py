import sys

from invoke import run, task


@task
def docs(watch=False, warn=False):
    if watch:
        return watcher(docs)
    run('make -C docs/ html', warn=warn)


@task
def test(coverage=False, watch=False, warn=False):
    if watch:
        return watcher(test, coverage=coverage)
    cmd = 'nosetests'
    if coverage:
        cmd += (
            ' --with-coverage --cover-package=spotify'
            ' --cover-branches --cover-html')
    run(cmd, pty=True, warn=warn)


@task
def preprocess_header():
    run('cpp -nostdinc spotify/api.h > spotify/api.processed.h || true')


@task
def update_authors():
    # Keep authors in the order of appearance and use awk to filter out dupes
    run("git log --format='- %aN <%aE>' --reverse | awk '!x[$0]++' > AUTHORS")


@task
def update_sp_constants():
    import spotify
    constants = [
        '%s,%s\n' % (attr, getattr(spotify.lib, attr))
        for attr in dir(spotify.lib)
        if attr.startswith('SP_')]
    with open('docs/sp-constants.csv', 'w+') as fh:
        fh.writelines(constants)


def watcher(task, *args, **kwargs):
    while True:
        run('clear')
        kwargs['warn'] = True
        task(*args, **kwargs)
        try:
            run(
                'inotifywait -q -e create -e modify -e delete '
                '--exclude ".*\.(pyc|sw.)" -r docs/ spotify/ tests/')
        except KeyboardInterrupt:
            sys.exit()
