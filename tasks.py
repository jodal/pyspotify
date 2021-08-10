from __future__ import print_function, unicode_literals

import shutil

from invoke import task


@task
def docs(ctx, warn=False):
    ctx.run("make -C docs/ html", warn=warn)


@task
def test(ctx, coverage=False, warn=False):
    cmd = "py.test"
    if coverage:
        cmd += " --cov=spotify --cov-report=term-missing"
    ctx.run(cmd, pty=True, warn=warn)


@task
def preprocess_header(ctx):
    ctx.run(
        'cpp -nostdinc spotify/api.h | egrep -v "(^#)|(^$)" '
        "> spotify/api.processed.h || true"
    )


@task
def update_authors(ctx):
    # Keep authors in the order of appearance and use awk to filter out dupes
    ctx.run("git log --format='- %aN <%aE>' --reverse | awk '!x[$0]++' > AUTHORS")


@task
def update_sp_constants(ctx):
    import spotify

    constants = [
        "%s,%s\n" % (attr, getattr(spotify.lib, attr))
        for attr in dir(spotify.lib)
        if attr.startswith("SP_")
    ]
    with open("docs/sp-constants.csv", "w+") as fh:
        fh.writelines(constants)


@task
def mac_wheels(ctx):
    """
    Create wheel packages compatible with:

    - macOS 10.6+
    - 32-bit and 64-bit
    - Apple-Python, Python.org-Python, Homebrew-Python

    Based upon https://github.com/MacPython/wiki/wiki/Spinning-wheels
    """

    versions = [
        # Python.org Python 2.7 for macOS 10.6 and later
        "/Library/Frameworks/Python.framework/Versions/2.7/bin/python",
        # Python.org Python 3.7 for macOS 10.6 and later
        "/Library/Frameworks/Python.framework/Versions/3.7/bin/python3",
        # Homebrew Python 2.7
        "/usr/local/bin/python2.7",
        # Homebrew Python 3.7
        "/usr/local/bin/python3.7",
    ]

    # Build wheels for all Python versions
    for executable in versions:
        shutil.rmtree("./build", ignore_errors=True)
        ctx.run("%s -m pip install wheel" % executable)
        ctx.run("%s setup.py bdist_wheel" % executable)

    # Bundle libspotify into the wheels
    shutil.rmtree("./fixed_dist", ignore_errors=True)
    ctx.run("delocate-wheel -w ./fixed_dist ./dist/*.whl")

    print("To upload wheels, run: twine upload fixed_dist/*")
