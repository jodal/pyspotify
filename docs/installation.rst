Installation
============


.. highlight: shell

Debian package
--------------

For Ubuntu and Debian users, *pyspotify* can be found in the ``python-spotify``
package of the `Mopidy APT archive <http://apt.mopidy.com/>`_.

Arch Linux package
------------------

Install the ``pyspotify-git`` package from the AUR.

Using PIP
---------

The ``pip`` program for installing Python packages is usually found is the
``python-pip`` package of your linux distribution. 
To install ``pyspotify``, run as root::

    # pip install -U pyspotify

To update an existing installation, simply use the same command.

Using setuptools (latest git version)
-------------------------------------

You will have first to clone the `git repository <http://github.com/mopidy/pyspotify>`_.

On Ubuntu or other Debian-based distributions::

    # python setup.py install --install-layout=deb

On other::

    # python setup.py install
