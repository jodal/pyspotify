************
Contributing
************

Contributions to pyspotify are welcome! Here are some tips to get you started
hacking on pyspotify and contributing back your patches.


Development setup
=================

1. Make sure you have the following Python versions installed:

   - CPython 2.7
   - CPython 3.2
   - CPython 3.3
   - PyPy 2

   If you're on Ubuntu, the `Dead Snakes PPA
   <https://launchpad.net/~fkrull/+archive/deadsnakes>`_ has packages of both
   old and new Python versions.

2. On Debian/Ubuntu, make sure you have `apt.mopidy.com
   <https://apt.mopidy.com/>`_ in your APT sources. Otherwise, install
   libspotify from source yourself.

3. Install Python, libffi, and libspotify development files. On Debian/Ubuntu::

       sudo apt-get install python-all-dev python3-all-dev libffi-dev libspotify-dev

4. Create and activate a virtualenv::

       virtualenv ve
       source ve/bin/activate

5. Install development dependencies::

       pip install cffi mock nose tox

6. Run tests.

   For a quick test suite run, using the virtualenv's Python version::

       nosetests

   For a complete test suite run, using all the Python implementations::

       tox


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

- Send a pull request to the ``v2.x/develop`` branch. See the `GitHub pull
  request docs <https://help.github.com/articles/using-pull-requests>`_ for
  help.


Additional resources
====================

- IRC channel: ``#mopidy`` at `irc.freenode.net <http://freenode.net/>`_

- `Issue tracker <https://github.com/mopidy/pyspotify/issues>`_

- `Mailing List <https://groups.google.com/forum/?fromgroups=#!forum/mopidy>`_

- `GitHub documentation <https://help.github.com/>`_

- `libspotify documentation
  <https://developer.spotify.com/technologies/libspotify/>`_
