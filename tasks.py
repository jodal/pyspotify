from __future__ import print_function, unicode_literals

import shutil
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
    cmd = 'py.test'
    if coverage:
        cmd += ' --cov=spotify --cov-report=term-missing'
    run(cmd, pty=True, warn=warn)


@task
def preprocess_header():
    run(
        'cpp -nostdinc spotify/api.h | egrep -v "(^#)|(^$)" '
        '> spotify/api.processed.h || true')


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


@task
def mac_wheels():
    """
    Create wheel packages compatible with:

    - OS X 10.6+
    - 32-bit and 64-bit
    - Apple-Python, Python.org-Python, Homebrew-Python

    Based upon https://github.com/MacPython/wiki/wiki/Spinning-wheels
    """

    prefix = '/Library/Frameworks/Python.framework/Versions'
    versions = [
        ('2.7', ''),
        ('3.4', '3'),
    ]

    # Build wheels for all Python versions
    for version, suffix in versions:
        run('%s/%s/bin/pip%s install -U pip wheel' % (prefix, version, suffix))
        shutil.rmtree('./build', ignore_errors=True)
        run('%s/%s/bin/python%s setup.py bdist_wheel' % (
            prefix, version, suffix))

    # Bundle libspotify into the wheels
    shutil.rmtree('./fixed_dist', ignore_errors=True)
    run('delocate-wheel -w ./fixed_dist ./dist/*.whl')

    print('To upload wheels, run: twine upload fixed_dist/*')
