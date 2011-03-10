# Drink! Quickstart

[TOC]

Drink! is a generic web+database framework, CMS oriented. It allows you to run a full website serving web pages, files of arbitrary size and dynamic applications.

It includes simple (but efficient) objects that can be configured and extended.

In the program, **page** and **element** are the same thing -- for clarity I will refer to *currently displayed element/page* as **current page** and *"children" elements/pages* as **page's elements**.

## Standard actions (top banner icons)

### General

![](/static/actions/exit.png) Log out
:  Closes your user session.

![](/static/actions/personal.png) Account settings
:  Edit your settings (name, password, email, etc...).

![](/static/actions/find.png) Search
:  Performs a full text search on the whole website.
:  The "fast" search will only match titles, otherwise it will search the content as well.

![](/static/actions/top.png) Back to parent element
:  Jumps one level up.

![](/static/actions/edit.png) Edit current page
:  Edit currently displayed page.

![](/static/actions/open.png) List content
:  View currently displayed page in *list* mode.

> **NOTE**: In *list* mode, you can add any computer-file content directly by drag & dropping it to the web page (over the *"you can drop files here"* text).

### Children elements

![](/static/actions/new.png)
:  Adds a new children element to currently displayed page.

![](/static/actions/edit.png)
:  Keep the mouse over an item in list mode and click on this icon to edit an element properties

![](/static/actions/delete.png)
:  Keep the mouse over an item in list mode and click on this icon to remove an element

## Element types

![](/static/mime/tasks.png) TODO list
:  Contains a list of tasks to complete

![](/static/mime/folder.png) Folder index
:  Folder-like display, with user-defined order.
:  You can drag & drop elements to change their order.
:  Beware `Ctrl` key must be pressed while you release left mouse button,
:  this is to prevent wrong moves.


![](/static/mime/markdown.png) Web page
:  This is a generic HTML or  [Markdown](http://daringfireball.net/projects/markdown/basics "Markdown") page.
:  Read [editor help](#editor) to know more about document edition.

![](/static/mime/page.png) WebFile
:  This Element can store any uploaded file from your computer, and attaches a description to it.
:  By default, it shows the user a download link, which is just a link to `/raw` URL element.
:  It can display some files too like images and texts.


<a id="editor"></a>
## Web page (Markdown) Editor

Click on the ![V](/static/markitup/sets/markdown/images/preview.png) to see an almost realtime preview.

Most icons are self-explicit, feel free to try them.

### Shortcuts
Here is a list of most common shortcuts:

* `Ctrl+B` : **Bold**
* `Ctrl+I` : *Italic*
* `Ctrl+P` : Insert picture
* `Ctrl+L` : Insert link
* `Ctrl+1` : Make level 1 title (top level)
* `Ctrl+2` : Make level 2 title
* `Ctrl+3` : etc... (until 6, the lowest, less important level)
* `Ctrl+ENTER` : Save & Exit

### Syntax

Get a complete description of the syntax [here](http://daringfireball.net/projects/markdown/syntax).

### Extensions to markdown

**Wiki mode**

You can automatically create a new *web page* by using *double brackets wiki-links like:

    [[this one]]

displayed like

[[this one]]

It will create a page called "this one" & and show you a page to edit the content on first access. On next access, it will be a simple link to the page.

**Descriptions**

With this syntax:

    definition of life
    : Life is quite complex
    : It can contains multi-line texts

You get:

definition of life
: Life is quite complex
: It can contains multi-line texts

**litteral blocks**

You can use this syntax:

    ~~~~~
    THIS SHOULD BE fixed case text
    ~~~~~

    ~~~
    iiiiiiiiOOOOOOOOiiiiiiOOOOO
    ~~~


To get:

~~~~~
THIS SHOULD BE fixed case text
~~~~~

~~~
iiiiiiiiOOOOOOOOiiiiiiOOOOO
~~~

Or, alternatively, you can enable highlight to standard code block mode (just indent the code):

~~~
    #!python
    def drink_is_fun():
        print "Oh yeah!"
~~~

Will produce

    #!python
    def drink_is_fun():
        print "Oh yeah!"

**TOC**

You can produce a simple *Table of contents* from your document's headings using:

    [TOC]

It's preferable to keep this at the beginning of the document but you are totally free.

## Access control

### Presentation

Access is granted by some simple rules, applied **per element**:

* **O**wner can do anything
* People in **r**ead group can view document/element
* People in **w**rite group can change document and **a**dd elements (but not its access rules)
* The special group **users** means *"any recognized user"*
* The special group **anonymous** means *"anybody connecting to the website"*
* Every user have his own group
* If someone is not explicitly listed in *write group*, then he can't **a**dd something but only **w**rite the current document.

Last but not least, after the common **r**ead, **w**rite, **a**ppend permissions, there is the **t**raversal access for people that can only access to children elements without permission to view traversed elements...

### Quick settings

This is some commonly used shortcuts to quickly set most of the access.

Private document
:  Nobody can access this document

Users can only consult
:  Any user recognized by the system can view the content

Users can change content
:  Any user recognized by the system can edit the document

Everybody can see
:  Any user (even anonymous - not logged in) can view the document

### Every user's permissions (wrta)
This is a world containing letters from **wrta**

**w**
:  write
**r**
:  read
**t**
:  traverse
**a**
:  add / append

Those permissions will be given to anybody, unconditionally.
