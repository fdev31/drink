from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink
from drink.types import dt2str, dt2ts

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
            txt = "(%s) %s"%(dt2str(self.date), txt)

        return txt

    date = ''

    def event(self):
        drink.response.headers['Content-Type'] = 'application/json'

        return {
            #'id': abs(int(hash(self.id))),
            'title': self.title,
            #'start': "%02d-%02d-%04d"%(self.date.year, self.date.month, self.date.day),
            'start': self.date.isoformat(),
            #'allDay': False,
            'url': self.path+'edit',
        }


class TODOList(drink.Page):

    description = "A TODO list"

    classes = {'TODO': TODO}

    mime = "tasks"

    css = ['/static/fullcalendar.css']

    js = ['/static/fullcalendar.min.js', '/static/tasks.js']

    html = '<div id="calendar"></div>'

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'description': drink.types.Text('Description'),
    }

    def events(self):
        import json

        return json.dumps([e.event() for e in self.itervalues()])

        start = drink.request.GET['start']
        end = drink.request.GET['end']
        print start, end
        return {}

exported = {'TODO list': TODOList}
