***********
Development
***********

Development of pyspotify is coordinated through the IRC channel ``#mopidy`` at
``irc.freenode.net`` and through `GitHub <http://github.com/>`_.


Code style
==========

For C code, follow the style of the Python C API, as outlined in :pep:`7`.

For Python code, follow `Mopidy's
<http://www.mopidy.com/docs/master/development/contributing/#code-style>`_
style.


Commit guidelines
=================

- We follow the development process described at http://nvie.com/git-model.

- Keep commits small and on topic.

- If a commit looks too big you should be working in a feature branch not a
  single commit.

- Merge feature branches with ``--no-ff`` to keep track of the merge.


Running tests
=============

To run tests, you need to install the ``nose`` test runner. On Ubuntu::

    sudo apt-get install python-nose

Using Pip::

    sudo pip install nose

Then you can build pyspotify and run ``nosetests``::

    rm -rf build/
    python setup.py build --with-mock
    PYTHONPATH=$(echo build/lib.linux-*/) nosetests


Continuous integration server
=============================

We run a continuous integration (CI) server at http://ci.mopidy.com/ that runs
all test on multiple platforms (Ubuntu, OS X, etc.) for every commit we push to
GitHub.

In addition to running tests, the CI server also gathers coverage statistics
and uses pylint to check for errors and possible improvements in our code. So,
if you're out of work, the code coverage and pylint data at the CI server
should give you a place to start.


Writing documentation
=====================

To write documentation, we use `Sphinx <http://sphinx.pocoo.org/>`_. See their
site for lots of documentation on how to use Sphinx. To generate HTML or LaTeX
from the documentation files, you need some additional dependencies.

You can install them through Debian/Ubuntu package management::

    sudo apt-get install python-sphinx

Then, to generate docs::

    cd docs/
    make        # For help on available targets
    make html   # To generate HTML docs

The documentation at http://pyspotify.mopidy.com/ is automatically updated when
a documentation update is pushed to ``mopidy/pyspotify`` at GitHub.


Creating releases
=================

#. Update changelog and commit it.

#. Merge the release branch (``develop`` in the example) into ``master``::

    git checkout master
    git merge --no-ff -m "Release v1.2.0" develop

#. Tag the release::

    git tag -a -m "Release v1.2.0" v1.2.0

#. Push to GitHub::

    git push
    git push --tags

#. Build package and upload to PyPI::

    git clean -fdx
    python setup.py sdist upload

#. Spread the word.
