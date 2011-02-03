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
            return drink.abort(401, "Not authorized")

        content = drink.request.GET.get('text')
        t = Task(sha1(content or str(time.time())).hexdigest(), self.path, content)
        self[t.id] = t
        transaction.commit()
        return t.id

    def rm(self):
        if 'w' not in drink.request.identity.access(self):
            return drink.abort(401, "Not authorized")

        tid = drink.request.GET.get('id')
        del self[tid]
        transaction.commit()
        return 'ok'

    # FIXME: rewrite, this should be default "add" method
    def edit(self):
        if 'w' not in drink.request.identity.access(self):
            return drink.abort(401, "Not authorized")

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

    def __init__(self, name, rootpath, content=''):
        drink.Model.__init__(self, name, rootpath)
        self.content = content
        self.created_on = time.time()

    def edit(self):
        return drink.Model.edit(self)

    def view(self):
        return '<div id="%(id)s">%(text)s</div>'%self.get()

    def struct(self):
        return {
            'id': self.id,
            'text': self.content,
        }

exported = {'Task list': TasksPage}
