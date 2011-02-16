Drink
=====

Alpha Web framework & sample mini CMS application with little dependencies: ZODB , bottle & markdown.
Aims to be quite generic "all-in-one-but-minimalistic" web+database framework.

The main ideas behind
---------------------

It should handle most of javascript, html & forms creation for you, for very fast prototype implementation.

Then you'r free to put your hands into html/css/js and customize to your precise requirements.

Goals
+++++

 - Add features at ONE place in ONE language (html/css/js may be required for some advanced/custom usages)
 - Be fast
 - Ajax (ajaj in fact) - with nice fallbacks for old browsers
 - No SQL
 - Website: as simple as a nested dict-like objects tree, endpoints (last element of URL) are object's properties & methods
 - Make it as productive as possible for most generic tasks

Out of the box, it is something between a wiki and a cms, probably a good base for a lightweight web CMS / Intranet / Forum / etc...

Main Features
-------------

* Zope/Bluebream -like at micro-framework sauce
* Designed to be simple, little knowledge involved
* Automatic object edition's form generation
* Multi-user with access control (group based)
* Very user friendly (once doc will be there...)
* Webpage edition live preview, client-side form validation
* Comes with some pre-developped objects:
  
  - folder index (sortable with D&D)
  - file (upload your own file, also allows D&D)
  - Web page ( markdown only )
  - Simple TODO list/TODOs (WIP)

  And of course special elements like Groups & Users ....

Issues
------

 * no documentation yet
 * not very well tested
 * not very powerful yet

