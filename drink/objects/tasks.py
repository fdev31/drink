from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink

class TODO(drink.Page):

    description = "Something to do"

    mime = "note"

    default_action = "edit"

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'content': drink.types.TextArea("Summary", group="b"),
        'description': drink.types.Text('Description'),
        #'date': drink.types.Date,
    }

    content = ''


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
