==========================
Developpers' documentation
==========================

.. currentmodule:: drink

Routing
-------

See drink as a tree of items stored in a database.
Since the database is structured (a single trunk, then branches, more branches etc... until "leafs", the children-most items),
it is easy to map it as HTTP URLs this way: http://domain.com/trunk/branch/sub-branch/sub-sub-branch/leaf

In our case, the trunk is "/" and the first "public" branch `id` is "pages". This way, most URLs will start with "/pages/". The final "/" indicates we want to access some item (or object or element, call it whatever you prefer). If there is no final *slash* at the end of the URL, then it's a item action or property (ex: *view*, *edit*, *list*, etc... or *struct*, *actions*, etc...).

This way, if you add an item called "My Calendar" under "Pages", the automatically-crafted url will be ``/pages/my-calendar/``, if you want to link directly to its *edit* form, then use ``/pages/my-calendar/edit``.
If you experiment some troubles, you probably made in inconsistant usage of trailing slash.

Database access
---------------

Objects can be safely retrieved (with permission checks) using :func:`drink.get_object`

Rendering
---------

All objects inheriting :class:`drink.Page` should implement a `view` method with
the same prototype as the default function which is :func:`drink.default_view`.

In case you need a simple but correct handling of unauthorized accesses, it is recommanded to return the value of :func:`drink.unauthorized` call in your handler. It will either show an error message or an authentication screen.

Text conversion
---------------

In case you have random kind of input (url encoded, latin string, utf-8 str, unicode) and want to ensure you can work with it as unicode data then you may use :func:`drink.omni`.

To render file sizes as readable strings for humans, just use :func:`drink.bytes2human`.


Adding upload capabilities
--------------------------

Creating a new uploadable type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, your page type you contain a properly filled :data:`~drink.Page.classes` property and the user must have permissions to add content to the desired :class:`~drink.Page`.

Then, your object must be registered using :func:`drink.add_upload_handler`.

API index
---------

Base classes
~~~~~~~~~~~~

.. autosummary::
   :toctree: apis

   Page
   ListPage

Base functions & data
~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: apis

   make_app
   classes
   get_object
   omni
   default_view
   add_upload_handler
   request
   response
   bytes2human
   db
   unauthorized
   init

Database backends
~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: apis

   zdb
   dumbdb

WSGI Building block
~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: apis

   make_app

Properties types
~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: apis

   types
   objects.markdown.MarkdownEditor


Builtin object types
~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: drink.objects

.. autosummary::
   :toctree: apis

   generic.WebFile
   generic.Settings
   markdown.MarkdownPage
   tasks.TODO
   tasks.TODOList
   users.User
   users.UserList
   users.Group
   users.GroupList
   finder.ObjectBrowser
   filesystem.Filesystem
   sonic.SonicHome
