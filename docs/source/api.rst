API Reference
=============

.. currentmodule:: drink

Functions
---------

Database access
***************

Objects can be safely retrieved (with permission checks) using :func:`drink.get_object`

Jinja2 Template rendering
*************************

The main rendering method is accessible via :func:`drink.default_view`.

In case you need a simple but correct handling of unauthorized accesses, it is recommanded to return the value of :func:`drink.unauthorized` call in your handler. It will either show an error message or an authentication screen.

Text conversion
***************

In case you have random kind of input (url encoded, latin string, utf-8 str, unicode) and want to ensure you can work with it as unicode data then you may use :func:`drink.omni`.

To render file sizes as readable strings for humans, just use :func:`drink.bytes2human`.


.. toctree::
   :hidden:

   apis/drink.add_upload_handler
   apis/drink.get_object
   apis/drink.unauthorized
   apis/drink.default_view
   apis/drink.omni
   apis/drink.bytes2human

Base Page types
---------------

.. autosummary::
    :toctree: apis

    drink
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

