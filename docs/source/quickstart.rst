Quickstart
==========

Pre-requisites
**************

You should be able to execute a terminal emulator (like ``cmd.exe``, ``xterm``, etc...)
and have notions with python. Even if the steps are detailed, some experience with :pypi:`virtualenv` may help.

If you skip the virtual environment part, it
might require additional work on permissions.
Feel free to use :pypi:`virtualenvwrapper`.

Installing
**********

It is recommanded to use a :pypi`virtualenv` for your drink installation::

   % virtualenv --no-site-packages --distribute drink_env
   % . drink_env/bin/activate

Then, you can install drink, either from *PyPi* (``easy_install drink``) or
from sources::

   % wget -O master.zip https://github.com/fdev31/drink/zipball/master
   % unzip master.zip
   % cd fdev31-drink-*
   % python setup.py install

Creating a project
******************

Do not forget to activate your virtual environment:

   % . drink_env/bin/activate

And chose a folder of your own, that can hold several projects and run ``drink make``::

   % cd ~/web_apps/
   % drink make
   Project folder: test_project
   Additional python package with drink objects
   (can contain dots): test_extensions
   Ip to use (just ENTER to allow all):
   HTTP port number (ex: "80"), by default 0.0.0.0:5000 will be used:
   Objects to activate:
   a gtd-like tasklist - tasks : y
   a wiki-like web page in markdown format - markdown : y
   a tool to find objects in database - finder : y
   a filesystem proxy, allow sharing of arbitrary folder or static websites - filesystem : y
   Additional root item name (just ENTER to finish):
   Project created successfuly.

   You can now go into the /home/fab/web_apps/test_project folder and run

   - drink db (to start the database daemon)
   - drink run (to start the web server)

   If you run with DEBUG=1 in environment, templates and python code should reload automatically when changed.
   For static files changes, no restart is needed.

Running
*******

GO into the project folder (same name as you answered), and type ``drink start``::

   % cd ~/web_apps/test_project
   % drink start

Exploring
*********

Debug mode
----------

Running drink in debug mode just consists in setting the ``DEBUG`` environment
variable to ``1``. In this mode, you gain some features:

   - Python code reloads automatically (with a bit of luck...)
   - HTML Templates are reloaded on every access
   - You have a flood of messages about everything happening
   - You get a nice interactive debugger in case of programming errors

This can be set in two ways, by editing the ``drink.ini`` file and using **debug** as the server.backend, as shown by this snippet::

   [server]
   backend = debug

You can also set that behavior directly from the command line::

   % DEBUG=1 drink start

Important files
---------------

The database configurations is hold by ``database/zeo.conf``, you might want to read ZEO & Zope3 docs in google to know in what way you can customize this, but the defaults should
be fine.

Action's icons are in ``static/actions/`` folder, you can also replace ``static/page.css`` file if you want a custom CSS.

The ``templates/main.html`` file can be easily customized as well, but this folder is mainly interesting to add your own custom templates (``main.html`` should be a good base).

An empy python module is also created automatically to fit the informations you
gave at *make* time. Feel free to add your objects inside it, if you add a file ``blog_application`` to that folder, you need to activate it in the ``drink.ini`` file:

   [objects]
   markdown=
   blog_application=
