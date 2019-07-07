from __future__ import print_function, unicode_literals

import shutil
import sys

from invoke import task


@task
def docs(ctx, watch=False, warn=False):
    if watch:
        return watcher(ctx, docs)
    ctx.run('make -C docs/ html', warn=warn)


@task
def test(ctx, coverage=False, watch=False, warn=False):
    if watch:
        return watcher(ctx, test, coverage=coverage)
    cmd = 'py.test'
    if coverage:
        cmd += ' --cov=spotify --cov-report=term-missing'
    ctx.run(cmd, pty=True, warn=warn)


@task
def preprocess_header(ctx):
    ctx.run(
        'cpp -nostdinc spotify/api.h | egrep -v "(^#)|(^$)" '
        '> spotify/api.processed.h || true')


@task
def update_authors(ctx):
    # Keep authors in the order of appearance and use awk to filter out dupes
    ctx.run(
        "git log --format='- %aN <%aE>' --reverse | awk '!x[$0]++' > AUTHORS")


@task
def update_sp_constants(ctx):
    import spotify
    constants = [
        '%s,%s\n' % (attr, getattr(spotify.lib, attr))
        for attr in dir(spotify.lib)
        if attr.startswith('SP_')]
    with open('docs/sp-constants.csv', 'w+') as fh:
        fh.writelines(constants)


def watcher(ctx, task, *args, **kwargs):
    while True:
        ctx.run('clear')
        kwargs['warn'] = True
        task(*args, **kwargs)
        try:
            ctx.run(
                r'inotifywait -q -e create -e modify -e delete '
                r'--exclude ".*\.(pyc|sw.)" -r docs/ spotify/ tests/')
        except KeyboardInterrupt:
            sys.exit()


@task
def mac_wheels(ctx):
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
        ctx.run('%s/%s/bin/pip%s install -U pip wheel' % (
            prefix, version, suffix))
        shutil.rmtree('./build', ignore_errors=True)
        ctx.run('%s/%s/bin/python%s setup.py bdist_wheel' % (
            prefix, version, suffix))

    # Bundle libspotify into the wheels
    shutil.rmtree('./fixed_dist', ignore_errors=True)
    ctx.run('delocate-wheel -w ./fixed_dist ./dist/*.whl')

    print('To upload wheels, run: twine upload fixed_dist/*')
