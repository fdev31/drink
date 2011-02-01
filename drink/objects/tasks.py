from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink

class TasksPage(drink.Page):

    mime = "tasks"

    doc = "A Task list"

    css = [
        "/static/style.css",
        "/static/validate.jquery.js",
    ]

    js = [
        "/static/jquery.shoppingList.js",
        "/static/script.js",
    ]

    html = """
    <div><a href="../"><img class="icon" src="/static/back.png" />Exit!</a></div>

    <h1>Daily tasks</h1>
    <div class="shoppingList">
        <ul>
        </ul>
    </div>
    """

    def __init__(self, *args, **kw):
        self.name = None
        self.rootpath = None
        self.id = None
        drink.Page.__init__(self, *args, **kw)

    def struct(self):
        return [t.get() for t in self.itervalues()]

    def view(self):
        fmt  = drink.request.GET.get('format', 'html')
        if fmt == 'json':
            return dict(tasks=self.struct())
        return drink.template('main.html', obj=self, no_admin=True,
             js=self.js, css=self.css, html=self.html, authenticated=drink.authenticated())

    def add(self):
        t = Task(drink.request.GET.get('text'), rootpath=self.path)
        self[t.id] = t
        transaction.commit()
        return t.id

    def rm(self):
        tid = drink.request.GET.get('id')
        del self[tid]
        transaction.commit()
        return 'ok'

    def edit(self):
        tid = drink.request.GET.get('id')
        content = drink.request.GET.get('text')
        self[tid].content = content
        transaction.commit()
        return 'ok'


class Task(drink.Model):

    editable_fields = {
        'content': drink.Text(),
    }

    @property
    def path(self):
        return self.rootpath + self.id

    def __init__(self, content='', rootpath=''):
        self.id = sha1(content or str(time.time())).hexdigest()
        self.content = content
        self.rootpath = rootpath
        self.created_on = time.time()
        drink.Model.__init__(self)

    def view(self):
        return '<div id="%(id)s">%(text)s</div>'%self.get()

    def struct(self):
        return {
            'id': self.id,
            'text': self.content,
        }

exported = {'Task list': TasksPage}
