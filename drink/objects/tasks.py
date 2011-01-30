from __future__ import absolute_import
import transaction
import time
from .generic import Page, Text
from drink import request, template, authenticated, rdr
from drink.zdb import Model
from hashlib import sha1

class TasksPage(Page):

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
        Page.__init__(self, *args, **kw)

    def get(self):
        return [t.get() for t in self.itervalues()]

    def view(self):
        fmt  = request.GET.get('format', 'html')
        if fmt == 'json':
            return dict(tasks=self.get())
        return template('main.html', obj=self, no_admin=True,
             js=self.js, css=self.css, html=self.html, authenticated=authenticated())

    def add(self):
        t = Task(request.GET.get('text'), rootpath=self.path)
        self[t.id] = t
        transaction.commit()
        return t.id

    def rm(self):
        tid = request.GET.get('id')
        del self[tid]
        transaction.commit()
        return 'ok'

    def edit(self):
        tid = request.GET.get('id')
        content = request.GET.get('text')
        self[tid].content = content
        transaction.commit()
        return 'ok'


class Task(Model):

    editable_fields = {
        'content': Text(),
    }

    @property
    def path(self):
        return self.rootpath + self.id

    def __init__(self, content='', rootpath=''):
        self.id = sha1(content or str(time.time())).hexdigest()
        self.content = content
        self.rootpath = rootpath
        self.created_on = time.time()
        Model.__init__(self)

    def view(self):
        return '<div id="%(id)s">%(text)s</div>'%self.get()

    def get(self):
        return {
            'id': self.id,
            'text': self.content,
        }


exported = {'Task list': TasksPage}
