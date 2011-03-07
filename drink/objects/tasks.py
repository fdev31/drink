from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink

class TODO(drink.Page):

    description = "Something to do"

    mime = "note"

    default_action = "edit"

    content = ''

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'date': drink.types.Date("Scheduled for", group="b"),
        'content': drink.types.TextArea("Summary", group="c"),
        #'description': drink.types.Text('Short description', group="a"),
    }

    @property
    def description(self):
        if len(self.content) > 100:
            txt = self.content[:100].rsplit(None, 1)[0]+" ..."
        else:
            txt = self.content
        if self.date:
            txt = "(%s) %s"%(self.date, txt)

        return txt

    date = ''


class TODOList(drink.ListPage):

    description = "A TODO list"

    classes = {'TODO': TODO}

    mime = "tasks"

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'description': drink.types.Text('Description'),
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
