************
Contributing
************

Contributions to pyspotify are welcome! Here are some tips to get you started
hacking on pyspotify and contributing back your patches.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.5
   - CPython 3.6
   - CPython 3.7
   - PyPy2.7 6.0+
   - PyPy3.5 6.0+

   If you're on Ubuntu, the `Dead Snakes PPA
   <https://launchpad.net/~fkrull/+archive/deadsnakes>`_ has packages of both
   old and new Python versions.

2. Install the following with development headers: Python, libffi, and
   libspotify.

   On Debian/Ubuntu, make sure you have `apt.mopidy.com
   <https://apt.mopidy.com/>`_ in your APT sources to get the libspotify
   package, then run::

       sudo apt-get install python-all-dev python3-all-dev libffi-dev libspotify-dev

3. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

4. Install development dependencies::

       pip install -e ".[dev]

5. Run tests.

   For a quick test suite run, using the virtualenv's Python version::

       py.test

   For a complete test suite run, using all the Python implementations::

       tox

6. For some more development task helpers, install ``invoke``::

       pip install invoke

   To list available tasks, run::

       invoke --list

   For example, to run tests on any file change, run::

       invoke test --watch

   Or, to build docs when any file changes, run::

       invoke docs --watch

   See the file ``tasks.py`` for the task definitions.


Submitting changes
==================

- Code should be accompanied by tests and documentation. Maintain our excellent
  test coverage.

- Follow the existing code style, especially make sure ``flake8`` does not
  complain about anything.

- Write good commit messages. Here's three blog posts on how to do it right:

  - `Writing Git commit messages
    <http://365git.tumblr.com/post/3308646748/writing-git-commit-messages>`_

  - `A Note About Git Commit Messages
    <http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>`_

  - `On commit messages
    <http://who-t.blogspot.ch/2009/12/on-commit-messages.html>`_

- One branch per feature or fix. Keep branches small and on topic.

- Send a pull request to the ``v2.x/master`` branch. See the `GitHub pull
  request docs <https://help.github.com/articles/using-pull-requests>`_ for
  help.


Additional resources
====================

- `Issue tracker <https://github.com/jodal/pyspotify/issues>`_

- `GitHub documentation <https://help.github.com/>`_

- `libspotify downloads and documentation archive
  <https://mopidy.github.io/libspotify-archive/>`_
