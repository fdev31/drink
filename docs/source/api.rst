API Reference
=============

.. currentmodule:: drink

Functions
---------

Objects can be safely retrieved (with permission checks) using :func:`drink.get_object`

The main rendering method is accessible via :func:`drink.default_view`.

.. toctree::
   :hidden:

   apis/drink.add_upload_handler
   apis/drink.get_object
   apis/drink.default_view

Classes
-------

.. autosummary::
   :toctree: apis

   drink.Page
   drink.ListPage

Base Page types
---------------

.. autosummary::
    :toctree: apis

    drink.objects.generic
    drink.objects.filesystem
    drink.objects.finder
    drink.objects.tasks
    drink.objects.markdown
    drink.objects.users

Page's supported Properties
---------------------------

.. autosummary::
   :toctree: apis

   drink.types


Database related
----------------

.. autosummary::
   :toctree: apis

    drink.zdb
    drink.dumbdb
    drink.DB_PATH

Internal objects
----------------

.. autosummary::
    :toctree: apis

    drink.request
    drink.response
    drink.classes
    drink.config

..   Import directories
     ++++++++++++++++++

      `scss/`

      Contains CSS in Sass language

      `templates/`

      Contains Jinja2 templates

      `static/`

      Contains all file assets like javascript code, icons, etc...

