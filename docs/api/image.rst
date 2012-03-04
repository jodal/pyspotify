Image subsystem
***************

.. warning:: Spotify images support in **pyspotify** is not complete yet,
    use at your own risk, or take a look at the code.

The :class:`Image` class
========================
.. currentmodule:: spotify

.. class:: Image

  Image objects

  .. method:: add_load_callback()

     Add a load callback

  .. method:: data()

     Get image data

  .. method:: error()

     Check if image retrieval returned an error code

  .. method:: format()

     Get image format (currently only JPEG)

  .. method:: image_id()

     Get image ID

  .. method:: is_loaded()

     True if this Image has been loaded by the client

  .. method:: remove_load_callback()

     Remove a load callback
