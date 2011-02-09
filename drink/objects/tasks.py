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

    def view(self):
        drink.rdr(self.path+'edit')


class TODOList(drink.ListPage):

    doc = "A TODO list"

    classes = {'TODO': TODO}

    mime = "tasks"

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

exported = {'TODO list': TODOList}
