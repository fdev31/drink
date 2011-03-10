Drink
=====

Alpha Web framework & sample mini CMS application with little
dependencies: ZODB , bottle & markdown.

Aims to be quite generic *all-in-one-but-minimalistic* web+database
framework.

Getting started
---------------

Install
~~~~~~~

Use "easy\_install" or "pip" to get 'jinja2', 'markdown', 'ZODB3'
and 'whoosh' installed on your system. Additionally you can install
*paste* or *gevent* for better performances.

Example (at the DOS/Console/Shell prompt):

::

     easy_install -U markdown
     easy_install -U jinja2
     easy_install -U ZODB3
     easy_install -U whoosh

or, alternatively:

::

     pip install -U markdown
     pip install -U jinja2
     pip install -U ZODB3
     pip install -U whoosh

Then, fetch the source archive and unpack it:

::

     wget http://pypi.python.org/packages/source/d/drink/drink-0.0.9.tar.bz2
     tar jxvf drink-0.0.9.tar.bz2

Running
~~~~~~~

Just go into the unpacked drink directory and execute the "manage"
script:

::

     cd drink-0.0.9
     ./manage

If you run into troubles, try:

::

     DEBUG=1 ./manage

Getting sources/Contributing
----------------------------

See `GitHub page <http://github.com/fdev31/drink>`_.

The main ideas behind
---------------------

It should handle most of javascript, html & forms creation for you,
for very fast prototype implementation.

Then you'r free to put your hands into html/css/js and customize to
your precise requirements.

Some debugging middleware are supported, edit drink/settings.ini
for details.

Goals
~~~~~


-  Add features at ONE place in ONE language (html/css/js may be
   required for some advanced/custom usages)
-  Be fast, with built-in search engine
-  Ajax (ajaj in fact) - with nice fallbacks for old browsers
-  No SQL
-  Website: as simple as a nested dict-like objects tree, endpoints
   (last element of URL) are object's properties & methods
-  Make it as productive as possible for most generic tasks

Out of the box, it is something between a wiki and a cms, probably
a good base for a lightweight web CMS / Intranet / Forum / etc!

Main Features
-------------


-  Built-in search engine
-  Multi-user with access control (group based) at each level
-  Automatic *views* and javascript-friendly requests, with regard
   to each object permissions
-  Automatic object edition's form generation
-  Webpage edition live preview, client-side form validation
-  Comes with some pre-developped objects:

   
   -  folder index (sortable with D&D)
   -  file (upload your own file, also allows D&D)
   -  Web page ( markdown only )
   -  Simple TODO list/TODOs (WIP)

   And of course special elements like Groups & Users !.

-  Very user friendly (once doc will be there!)


Issues
------


-  no documentation yet (default manager account, login/password:
   ``admin/admin`` )
-  no auto tests yet
-  not very powerful yet

Release changes
---------------


-  Add a nice Help by default
-  Basic *date* type (used in TODO example object), will pop a
   calendar up in edit form
-  Renamed File to "WebFile"
-  Better web 2.0 experience
-  Support for web-editable default actions on objects (avoids
   redirects)
-  Add a custom wsgi loader that gracefully loads the fastest
   compatible wsgi backend available
-  Finder now also deletes traces of old objects
-  Add support for *"full"* search in finder
-  Add Indent/Deindent support to Markdown editor
-  As always: Fixes & Bugs

Roadmap
-------

0.1 (wip)
~~~~~~~~~


-  abstract all low-level models (blobs...)
-  review 401 handling, ask for login/passwd in case of new session
-  fix markdown preview css (make it seamless)
-  add calltips everywhere
-  change cookie on password change
-  pack should call
   http://packages.python.org/Whoosh/api/index.html?highlight=optimize#whoosh.index.Index.optimize
   on whoosh
-  only accept object move if it succeded on server
-  allow custom extensions
-  default content for every user
-  allow rss via
   http://www.freewisdom.org/projects/python-markdown/RSS
-  HomePage object: Login-splash+UserDashboard write user homepages
   (with login & passwd & name & surname change) / splash-like if not
   logged-in
-  allow objects to add custom actions in admin bar
-  think about comments ( as property of some Model ?) -
   commentlist ?
-  edit form: only send "dirty" values when possible
-  add some recursive permissions setter
-  improve task list
-  "background processes" for each user / sessions
-  theme support (config entry + template & static path)
-  add more types to default form edition
   
   -  object\_path

-  find the cleanest way to make all incoming URLs ends with /
-  add proper checks at server side too (in add & edit methods
   mostly)
-  Form object?

Fixes:


-  /users as user => 401 (should list instead)
-  search => 401 by default (should be allowed)
-  mask file upload widget if File not available here
-  investigate fileupload D&D bugs
-  files >4GB are making crazy js loops
-  files ~>500MB may hang the request & cause timeout

0.2
~~~


-  zip importer
-  pdf with pypdf
-  doc
-  project support (using drink as a base)
-  integrate imgviewer (image folder type)

0.3
~~~


-  multi-object page

0.4
~~~


-  chat program

0.5
~~~


-  forum

0.6
~~~


-  gadgets (google search, rss reader, clock, xkcd, ?)

0.7
~~~


-  permissions setting admin object

0.8
~~~


-  user interface cleanup

0.9
~~~


-  doc & fix but minor improvements

1.0
~~~


-  stable release

1.x
~~~


-  homepage /user pages focus


