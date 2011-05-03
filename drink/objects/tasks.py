from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink
import json
from datetime import timedelta, date, datetime
from drink.types import dt2str, dt2ts

class TODO(drink.Page):

    description = "Something to do"

    mime = "note"

    default_action = "edit"

    content = ''

    all_day = True

    duration = 1

    start_time = '10:00'

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'all_day': drink.types.BoolOption("All Day", group="b"),
        'date': drink.types.Date("Scheduled for", group="b"),
        'start_time': drink.types.Text("Start time", group="b"),
        'duration': drink.types.Float("Duration (hours)", group="b"),
        'content': drink.types.TextArea("Summary", group="c"),
        #'description': drink.types.Text('Short description', group="a"),
    }

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.date = date.today()

    @property
    def html(self):
        return '<div><h2>%(title)s</h2><p class="comment">%(date)s at %(start_time)s for %(duration)s hours</p><p class="description">%(content)s</p></div>'%self.__dict__

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
        # TODO: improve this line
        start_hour, start_min = (int(x.strip()) for x in self.start_time.split(':'))
        days, minutes = divmod(float(self.duration), 24)
        seconds = minutes*3600
        start = datetime(self.date.year, self.date.month, self.date.day, start_hour, start_min)

        return {
            'id': self.id,
            'title': self.title,
            'start': start.isoformat(),
            'end': (start + timedelta(days, seconds)).isoformat(),
            'allDay': self.all_day,
            'path': self.path,
            'description': self.content,
        }


class TODOList(drink.Page):

    description = "A TODO list"

    classes = {'TODO': TODO}

    mime = "tasks"

    css = ['/static/fullcalendar.css']

    js = ['/static/fullcalendar.min.js', '/static/tasks.js']

    html = '<div id="calendar"></div>'

    gmail_login = ""
    gmail_password = ""

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'gmail_login': drink.types.Text("Gmail login", group="gmail"),
        'gmail_password': drink.types.Text("Gmail password", group="gmail", type="password"),
        'description': drink.types.Text('Description'),
    }

    def events(self):
        l = [e.event() for e in self.itervalues()]
        try:
            l.extend(self.get_gmail_events())
        except Exception, e:
            print e

        return json.dumps(l)

    def get_gmail_events(self):
        #https://www.google.com/calendar/feeds/default/allcalendars/full
        #try:
            #from xml.etree import ElementTree
        #except ImportError:
            #from elementtree import ElementTree
        #import gdata.calendar.data
        import gdata.calendar.client
        #import gdata.acl.data
        #import atom.data
        #import time

        client = gdata.calendar.client.CalendarClient(source='Free-Drink-v1')
        client.ClientLogin(self.gmail_login, self.gmail_password, client.source)

        #feed  = client.GetAllCalendarsFeed()
        #print feed.title.text
        #for i, a_calendar in enumerate(feed.entry):
            #print '\t%s. %s' % (i, a_calendar.title.text,)

        start = datetime.fromtimestamp(float(drink.request.GET['start']))
        end = datetime.fromtimestamp(float(drink.request.GET['end']))

        def DateRangeQuery(calendar_client, start_date='2007-01-01', end_date='2007-07-01'):
            print 'Date range query for events on Primary Calendar: %s to %s' % (start_date, end_date,)
            query = gdata.calendar.client.CalendarEventQuery()
            query.start_min = start_date
            query.start_max = end_date
            query.max_results = 100
            feed = calendar_client.GetCalendarEventFeed(q=query)
            for i, an_event in enumerate(feed.entry):
                yield {
                    'id': an_event.id.text,
                    'title': an_event.title.text,
                    'start': an_event.when[0].start,
                    'end': an_event.when[0].end,
                    'allDay': False,
                    'href': an_event.link[0].href,
                    'description': an_event.content.text,
                }

        return list(DateRangeQuery(client, start.isoformat(), end.isoformat()))

exported = {'TODO list': TODOList}
