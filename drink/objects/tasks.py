from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink

class TODO(drink.Page):

    doc = "Something to do"

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'content': drink.types.TextArea("Summary", group="b"),
        #'date': drink.types.Date,
    }

    content = ''
    title = ''

    def __init__(self, name, root):
        drink.Page.__init__(self, name, root)

    def view(self):
        drink.rdr(self.path+'edit')


class TODOList(drink.ListPage):

    doc = "A TODO list"

    classes = {'TODO': TODO}

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
    }

    html = """
    <div><a href="../"><img class="icon" src="/static/back.png" />Exit!</a></div>

    <h1>Daily tasks</h1>
    <div class="shoppingList">
        <ul>
        </ul>
    </div>
    """



class TasksPage(drink.Page):

    mime = "tasks"

    doc = "A Task list"

    css = [
        "/static/style.css",
    ]

    js = [
        "/static/jquery.shoppingList.js",
        "/static/script.js",
    ]

    title = "A task lsit"

    html = """
    <div><a href="../"><img class="icon" src="/static/back.png" />Exit!</a></div>

    <h1>Daily tasks</h1>
    <div class="shoppingList">
        <ul>
        </ul>
    </div>
    """

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.name = name

    def struct(self):
        return [t.struct() for t in self.itervalues()]

    def view(self):
        fmt  = drink.request.GET.get('format', 'html')
        if fmt == 'json':
            return dict(tasks=self.struct())
        return drink.template('main.html', obj=self, no_admin=True,
             js=self.js, css=self.css, html=self.html, authenticated=drink.request.identity)

    def add(self):
        if 'w' not in drink.request.identity.access(self):
            return drink.abort(401, "Additions Not authorized")

        content = drink.request.GET.get('text')
        t = Task(sha1(content or str(time.time())).hexdigest(), self.path, content)
        self[t.id] = t
        transaction.commit()
        return t.id

    def rm(self):
        if 'w' not in drink.request.identity.access(self):
            return drink.abort(401, "Deletion Not authorized")

        tid = drink.request.GET.get('id')
        del self[tid]
        transaction.commit()
        return 'ok'

    # FIXME: rewrite, this should be default "add" method
    def edit(self):
        if 'w' not in drink.request.identity.access(self):
            return drink.abort(401, "Edition Not authorized")

        tid = drink.request.GET.get('id')
        content = drink.request.GET.get('text')
        self[tid].content = content
        transaction.commit()
        return 'ok'


class Task(drink.Model):

    editable_fields = {
        'content': drink.types.Text(),
    }

    @property
    def title(self):
        if len(self.content) > 20:
            return self.content[:20]+"..."
        else:
            return self.content

    @property
    def path(self):
        return self.rootpath + self.id

    def __init__(self, name, rootpath, content=''):
        drink.Model.__init__(self, name, rootpath)
        self.content = content
        self.created_on = time.time()

    def view(self):
        return '<div id="%(id)s">%(text)s</div>'%self.get()

    def struct(self):
        return {
            'id': self.id,
            'text': self.content,
        }

exported = {'Task list': TasksPage, 'TODO list': TODOList}
