# Drink

Alpha Web framework & sample mini CMS.

Aims to be quite generic *all-in-one-but-minimalistic* web+database high-level framework.

Take a look at the (WIP) [documentation at drink.rtfd.org](http://drink.readthedocs.org/en/latest/).

## Dependencies

Use "easy_install" or "pip" to get 'jinja2', 'markdown', 'ZODB3' and 'whoosh' installed on your system.
Additionally you can install *paste* or *gevent* for better performances.

Example (at the DOS/Console/Shell prompt):

     easy_install -U markdown

 or, alternatively:

     pip install -U markdown

Dependencies list:

- markdown
- jinja2
- ZODB3
- whoosh
- fs

### Install

Just fetch the source archive and unpack it:

     wget http://pypi.python.org/packages/source/d/drink/drink-DRINK_VERSION.tar.bz2
     tar jxvf drink-DRINK_VERSION.tar.bz2

### Running

Just go into the unpacked drink directory and execute the "manage" script:

     cd drink-DRINK_VERSION
     ./manage

If you run into troubles, try:

     DEBUG=1 ./manage

## Getting sources/Contributing

See [GitHub page][].

## The main ideas behind

It should handle most of javascript, html & forms creation for you, for
very fast prototype implementation.

Then you'r free to put your hands into html/css/js and customize to your
precise requirements.

Some debugging middleware are supported, edit drink/settings.ini for details.

### Goals

-   Add features at ONE place in ONE language (html/css/js may be
    required for some advanced/custom usages)
-   Be fast, with built-in search engine
-   Ajax (ajaj in fact) - with nice fallbacks for old browsers
-   No SQL
-   Website: as simple as a nested dict-like objects tree, endpoints
    (last element of URL) are object's properties & methods
-   Make it as productive as possible for most generic tasks

Out of the box, it is something between a wiki and a cms, probably a
good base for a lightweight web CMS / Intranet / Forum / etc!

## Main Features

-   Built-in search engine
-   Multi-user with access control (group based) at each level
-   Automatic *views* and javascript-friendly requests, with regard to each object
    permissions
-   Automatic object edition's form generation
-   Webpage edition live preview, client-side form validation
-   Comes with some pre-developped objects:

    -   folder index (sortable with D&D)
    -   file (upload your own file, also allows D&D)
    -   Web page ( markdown only )
    -   Simple TODO list/TODOs (WIP)
    -   Filesystem mountpoint (alpha)

    And of course special elements like Groups & Users !.

-   Very user friendly (once doc will be there!)

## Issues

-   no documentation yet (default manager account, login/password:
    `admin/admin` )
-   no auto tests yet
-   not very powerful yet

## Current release changes

-   Text type can have different subtypes now (ex: password)
-   New type: Choice
-   Settings can be changed within drink
-   Gcalendar support for Calendar (+ extended Task object)
-   Jquery updated
-   Simple "duration" type
-   Javascript refactor
-   Introduction of a simple generic actions framework
-   D&Drop form is more integrated
-   Templates dropped support for static HTML, more and more content will come with js/jQuery + JSON
-   As always: Fixes & Bugs

## Roadmap

### 0.1 (wip)

- add more types to default form edition
   - object_path => integrate it to markdown editor
- generalize edit & _edit behavior, with a special return value
- standardize json answers {'success': true} or {'error': true, 'message': 'permission denied'} or {'redirect': url, \*\*kw}
- review 401 handling, ask for login/passwd in case of new session (to be finished)
- change cookie on password change => Create session cookie !
- handle per-owner "recycle bin", "changes log" & groups
- clean javascript to provide a library, allowing mobile detection & adaptation
- buildbot & virtualenv
- only accept object move if it succeded on server
- allow custom extensions
- Per-user group-list, showing in permissions panels (Authenticator will constitute a cache of sets with 'path': permission)
- allow rss via http://www.freewisdom.org/projects/python-markdown/RSS
- HomePage object: Login-splash+UserDashboard write user homepages (with login & passwd & name & surname change) / splash-like if not logged-in
- think about comments ( as property of some Model ?) - commentlist ?
- edit form: only send "dirty" values when possible
- add some recursive permissions setter
- "background processes" for each user / sessions
- theme support (config entry + template & static path)
- ensure proper checks are correct at server side
- Form object?
- pack should call http://packages.python.org/Whoosh/api/index.html?highlight=optimize#whoosh.index.Index.optimize on whoosh
- add calltips everywhere
- default content for every user
- Think about opening WebFiles in mail client as attached file...
- add markdown support to tasks comment
- improve link support (javascript popup) in markdown so it's easy to link tasks to any object

Fixes:

- only returns requested range in TODO List / generic solution to request range of child
- Rename Tasks/TODO List to calendar
- remove Ctrl+Enter conflict on Markitup
- /users as user => 401 (should list instead)
- search => 401 by default (should be allowed)
- investigated fileupload D&D bugs:
  - files >4GB are making crazy js loops
  - files ~>500MB may hang the request & cause timeout

### 0.2

- zip importer
- pdf with pypdf
- doc
- project support (using drink as a base)
- integrate imgviewer (image folder type)

### 0.3

- multi-object page
- spreadsheet ?
- integrate graph library (http://www.jqplot.com/)

### 0.4
- "real" sessions ?
- chat program (introduce webhooks ?)

### 0.5
- forum
- more tests

### 0.6
- gadgets (google search, rss reader, clock, xkcd, ?)

### 0.7
- permissions setting admin object

### 0.8
- user interface cleanup

### 0.9
- doc & fix but minor improvements

### 1.0
- stable release

### 1.x
- homepage /user pages focus


  [GitHub page]: http://github.com/fdev31/drink

