<a href="https://github.com/fdev31/drink"><img style="position: absolute; top: 0; left: 0; border: 0;" src="https://a248.e.akamai.net/assets.github.com/img/ce742187c818c67d98af16f96ed21c00160c234a/687474703a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f6c6566745f677261795f3664366436642e706e67" alt="Fork me on GitHub"></a>

# Drink

Alpha Web framework & sample mini CMS.

Aims to be quite generic *all-in-one-but-minimalistic* web+database high-level framework.

- [Documentation]
- [Bugtracker]
- [GitHub page]

## Dependencies

Additionally you can install *paste* or *gevent* for better performances,
the fastest backend will be used by default.
For "production" setups, I recommand using uwsgi, helper scripts are provided.

For the full dependencies list, open the [requirements.txt](https://github.com/fdev31/drink/blob/master/requirements.txt) file. Note that some requirements are not mandatory.

- ZODB has a fallback allowing you to test drink without any C extension.
- setproctitle can be missing
- repoze.debug and weberror are only developer's requirement and may be dropped in the future
- Paste guaranties a good experience, but uwsgi + nginx is definitely the killer combination

Even if it should be portable, Drink is currently only tested on Linux.

### Install

Just fetch the source archive and unpack it:

     wget http://pypi.python.org/packages/source/d/drink/drink-DRINK_VERSION.tar.bz2
     tar jxvf drink-DRINK_VERSION.tar.bz2

Then install it (as root/admin):

     cd drink-DRINK_VERSION
     python setup.py install

Alternatively, if you prefer to not install drink on your system, unix users will find a *make_project.sh* script at the root of the sources folder, more experienced users can just use *virtualenv*:

    cd drink-DRINK_VERSION
    virtualenv --no-site-packages drink_test_folder
    . drink_test_folder/bin/activate
    python setup.py install

### Create and run your drink project

Wherever you are on the virtual environment or directly accessing your system,
go to a folder of your choice (like "My Web Projects") and then type:

    drink make

Follow the instructions, here is a sample session:

    Project folder: my-cms
    Additional python package with drink objects
    (can contain dots): cms_extensions
    Ip to use (just ENTER to allow all):
    HTTP port number (ex: "80"), by default 0.0.0.0:5000 will be used:
    Objects to activate:
    a gtd-like tasklist - tasks : y
    a wiki-like web page in markdown format - markdown : y
    a tool to find objects in database - finder : y
    a filesystem proxy, allow sharing of arbitrary folder or static websites - filesystem : y
    Additional root item name (just ENTER to finish): Private
     0 - Folder index
     1 - WebFile
    Select the desired type index: 1
    Additional root item name (just ENTER to finish):
    Project created successfuly.

    You can now go into the /tmp/my-cms folder and run

    - drink db (to start the database daemon)
    - drink run (to start the web server)

    If you run with DEBUG=1 in environment, templates and python code should reload automatically when changed.
    For static files changes, no restart is needed.



To start drink application, the easiest way it to type:

    drink start

If you run into troubles, try:

     DEBUG=1 drink start

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

-   Css update, uses skeleton as base
-   uWSGI integration
-   Real passwords using hashing
-   D&Drop form is more integrated
-   Jquery updated, also Whoosh > 2.0 is required now
-   Introduction of a simple generic actions framework
-   Items are easily customizable in list mode as well (but not their actions yet)
-   Gcalendar support for Calendar (+ extended Task object)
-   New type: Choice, Duration (very basic)
-   Text type can have different subtypes now (ex: password)
-   Authentication now recovers your original location
-   Shortcuts/Keyboard navigation, press "h" to see help
-   Add an "in-memory" database, using pickles to save state (useful for testing purposes)
-   Templates dropped support for static HTML, more and more content comes with js/jQuery + JSON
-   Simplify easy permissions panel, also add possibility to add someone as "trusted" so it can inherit your permissions on documents
-   Javascript refactor started
-   As always: Fixes & Bugs

## Roadmap

### 0.1 (wip)

- add more types to default form edition
   - object_path => integrate it to markdown editor
- generalize edit & _edit behavior, with a special return value
- standardize json answers {'success': true} or {'error': true, 'message': 'permission denied'} or {'redirect': url, \*\*kw}
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
  [Documentation]: http://drink.readthedocs.org/en/latest/
  [Bugtracker]: https://github.com/fdev31/drink/issues
