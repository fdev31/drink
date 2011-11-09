==========================
Developpers' documentation
==========================


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
