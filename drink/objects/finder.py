from __future__ import absolute_import
import drink

class ObjectBrowser(drink.Page):
    mime = "search"

    doc = "A very basic object finder"

    classes = {}

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.lastlog = {}

    def query(self):
        yield '<html><body>'
        pat = drink.request.forms.get('pattern')
        items = []
        def _match(i, ignore_case=False):
            for attr in ('title', 'content', 'description'):
                v = getattr(i, attr, None)
                if isinstance(v, basestring):
                    if pat in v:
                        return True
            return False

        to_scan = drink.db.values()
        auth = drink.request.identity

        for item in to_scan:
            if 'r' in auth.access(item) and _match(item):
                items.append(item)
                yield '<li><a href="%s">%s</a></li>'%(item.path, item.title)
            try:
                to_scan.extend(item.itervalues())
            except AttributeError:
                pass
        self.lastlog[auth.id] = (pat, items)
        yield '<div>Done!</div><a href="%s">make new search...</a></body></html>'%self.path

    def view(self):

        auth = drink.request.identity

        if auth.id in self.lastlog:
            pat, items = self.lastlog[auth.id]
        else:
            pat = ''
            items = None


        form = ['<form class="query_form" id="query_form" action="query" method="post">',
            drink.types.Text('Look for').html('pattern', pat),
            '<input class="submit" type="submit" value="GO!"/></form>']
        if items:
            form.extend('<li><a href="%s">%s</a></li>'%(i.path, i.title) for i in items)

        return drink.template('main.html', obj=self, html='\n'.join(form), authenticated=auth, classes=self.classes)

exported = {"Finder": ObjectBrowser}
