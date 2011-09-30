from __future__ import absolute_import
import transaction
import time
from hashlib import sha1
import drink
from itertools import chain
from datetime import timedelta, date, datetime
from drink.types import dt2str, dt2ts

class TODO(drink.Page):

    description = u"Something to do"

    mime = "note"

    default_action = "edit"

    content = ''

    all_day = True

    duration = 1

    start_time = '10:00'

    auto_report = False

    editable_fields = {
        'title': drink.types.Text("Title", group="a"),
        'all_day': drink.types.BoolOption("All Day", group="b"),
        'date': drink.types.Date("Scheduled for", group="b"),
        'start_time': drink.types.Text("Start time", group="b"),
        'duration': drink.types.Duration("Duration (hours)", group="b"),
        'content': drink.types.TextArea("Summary", group="c"),
        'auto_report': drink.types.BoolOption("Can't lean in past", group="b"),
        #'description': drink.types.Text('Short description', group="a"),
    }

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.date = date.today()

    @property
    def html(self):
        return u'<div><h2>%(title)s</h2><p class="comment">%(date)s at %(start_time)s for %(duration)s hours</p><p class="description">%(content)s</p></div>'%self.__dict__

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
        try:
            start_hour, start_min = (int(x) for x in self.start_time.split(':'))
        except ValueError:
            start_hour = int(self.start_time)
            start_min = 0

        today = date.today()
        if self.auto_report and today > self.date:
            l_date = today
        else:
            l_date = self.date

        days, minutes = divmod(float(self.duration), 24)
        seconds = minutes*3600
        start = datetime(l_date.year, l_date.month, l_date.day, start_hour, start_min)

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

    drink_name = 'TODO list'

    description = u"A TODO list"

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
            import traceback
            traceback.print_exc()
            print "gmail_events: returning gracefuly"
        return drink.dumps(l)

    def get_gmail_events(self):
        import gdata.calendar.client
        client = gdata.calendar.client.CalendarClient(source='Free-Drink-v1')
        if not self.gmail_login:
            return
        client.ClientLogin(self.gmail_login, self.gmail_password, client.source)

        #feed  = client.GetAllCalendarsFeed()
        #print feed.title.text
        #for i, a_calendar in enumerate(feed.entry):
            #print '\t%s. %s' % (i, a_calendar.title.text,)

        if 'start' in drink.request.GET:
            start = datetime.fromtimestamp(float(drink.request.GET['start']))
        else:
            start = None

        if 'end' in drink.request.GET:
            end = datetime.fromtimestamp(float(drink.request.GET['end']))
        end = None

        def DateRangeQuery(calendar_client, feed_src=None, start_date=None, end_date=None):
            # FIXME !!
            if not start_date:
                start_date = '2007-01-01'
            if not end_date:
                end_date = '2012-01-01'

            print 'Date range query for events on Primary Calendar: %s to %s' % (start_date, end_date,)
            query = gdata.calendar.client.CalendarEventQuery()
            query.start_min = start_date
            query.start_max = end_date
            feed_entries = []
            for n in xrange(2):
                try:
                    feed_entries = calendar_client.GetCalendarEventFeed(uri=feed_src.link[0].href, q=query).entry
                except Exception:
                    pass
                else:
                    break

            for i, an_event in enumerate(feed_entries):
                #TODO: check "all day"
                yield {
                    'id': an_event.id.text,
                    'title': an_event.title.text,
                    'start': an_event.when[0].start,
                    'end': an_event.when[0].end,
                    'allDay': False,
                    'href': an_event.link[0].href,
                    'description': an_event.content.text,
                }

        all_feeds = getattr(self, '_v_all_feeds', None) or None

        # Try a gcalendar connection 2 times

        for n in xrange(2):
            try:
                all_feeds = client.GetAllCalendarsFeed().entry
                print "failed %d"%n
            except Exception:
                pass
            else:
                self._v_all_feeds = all_feeds
                break

        return chain(*(DateRangeQuery(client, feed,
            start.isoformat() if start else None,
            end.isoformat() if end else None)
            for feed in all_feeds))
