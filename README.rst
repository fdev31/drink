Drink
=====

Alpha Web framework & sample mini CMS application with little dependencies: ZODB , bottle & markdown.
Aims to be quite generic "all-in-one-but-minimalistic" web+database framework.

Getting sources/Contributing
----------------------------

See `GitHub page <http://github.com/fdev31/drink>`_.

The main ideas behind
---------------------

It should handle most of javascript, html & forms creation for you, for very fast prototype implementation.

Then you'r free to put your hands into html/css/js and customize to your precise requirements.

Goals
+++++

- Add features at ONE place in ONE language (html/css/js may be required for some advanced/custom usages)
- Be fast, with built-in search engine
- Ajax (ajaj in fact) - with nice fallbacks for old browsers
- No SQL
- Website: as simple as a nested dict-like objects tree, endpoints (last element of URL) are object's properties & methods
- Make it as productive as possible for most generic tasks

Out of the box, it is something between a wiki and a cms, probably a good base for a lightweight web CMS / Intranet / Forum / etc...

Main Features
-------------

* Designed to be simple, little knowledge involved
* Built-in search engine
* Automatic object edition's form generation
* Multi-user with access control (group based) at each level
* Automatic "views" of your content, with regard to each object permissions
* Webpage edition live preview, client-side form validation
* Comes with some pre-developped objects:

  - folder index (sortable with D&D)
  - file (upload your own file, also allows D&D)
  - Web page ( markdown only )
  - Simple TODO list/TODOs (WIP)

  And of course special elements like Groups & Users ....

* Very user friendly (once doc will be there...)

Issues
------

* no documentation yet (default manager account, login/password: ``admin/admin`` )
* no auto tests yet
* not very powerful yet

Release changes
---------------

* Allow [[wiki pages]] in Markdown pages
* Css & icons update
* Simplified user workflow for edition  
* All objects can be listed now
* Very simple factory to automatically create Markdown objects

