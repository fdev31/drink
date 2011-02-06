from __future__ import absolute_import
import drink

class ObjectBrowser(drink.Page):
    mime = "search"

    doc = "A very basic object finder"

    classes = {}

    def query(self):
        yield '<html><body>'
        pat = drink.request.forms.get('pattern')
        print pat
        def _match(i, ignore_case=False):
            print pat
            for attr in ('title', 'content', 'description'):
                v = getattr(i, attr, None)
                if isinstance(v, basestring):
                    if pat in v:
                        return True
            return False

        to_scan = drink.db.values()
        for item in to_scan:
            if _match(item):
                yield '<li><a href="%s">%s</a></li>'%(item.path, item.id)
            try:
                to_scan.extend(item.itervalues())
            except AttributeError:
                pass
        yield "<div>Done!</div></body></html>"

    def view(self):
        form= ['<form class="query_form" id="query_form" action="query" method="post">',
            drink.types.Text('Look for').html('pattern', ''),
            '<input class="submit" type="submit" value="GO!"/></form>']
        return drink.template('main.html', obj=self, html='\n'.join(form), authenticated=drink.request.identity, classes=self.classes)

exported = {"Finder": ObjectBrowser}
