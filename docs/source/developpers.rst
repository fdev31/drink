==========================
Developpers' documentation
==========================

Routing
-------

See drink as a tree of items stored in a database.
Since the database is structured (a single trunk, then branches, more branches etc... until "leafs", the children-most items),
it is easy to map it as HTTP URLs this way: http://domain.com/trunk/branch/sub-branch/sub-sub-branch/leaf

In our case, the trunk is "/" and the first "public" branch `id` is "pages". This way, most URLs will start with "/pages/". The final "/" indicates we want to access some item (or object or element, call it whatever you prefer). If there is no final *slash* at the end of the URL, then it's a item action or property (ex: *view*, *edit*, *list*, etc... or *struct*, *actions*, etc...).

This way, if you add an item called "My Calendar" under "Pages", the automatically-crafted url will be ``/pages/my-calendar/``, if you want to link directly to its *edit* form, then use ``/pages/my-calendar/edit``.
If you experiment some troubles, you probably made in inconsistant usage of trailing slash.

Rendering
---------

All objects inheriting :class:`drink.Page` should implement a `view` method with
the same prototype as the default function which is :func:`drink.default_view`.

Adding upload capabilities
--------------------------

Creating a new uploadable type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, your page type you contain a properly filled :data:`~drink.Page.classes` property and the user must have permissions to add content to the desired :class:`~drink.Page`.

Then, your object must be registered using :func:`drink.add_upload_handler`.
