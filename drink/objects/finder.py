from __future__ import absolute_import

import os
import drink
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser

INDEX_DIR = os.path.join(drink.DB_PATH, 'whoosh')
qparser = indexer = None


def init():
    global qparser, indexer

    if os.path.exists(INDEX_DIR):
        indexer = open_dir(INDEX_DIR)
    else:
        os.mkdir(INDEX_DIR)
        indexer = create_in(
            INDEX_DIR,
            Schema(path=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT)
        )

    qparser = QueryParser("title", schema=indexer.schema)

def reset():
    import shutil
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    init()

def extract_obj(o):
    return {'path': unicode(o.path),
        'title': unicode(o.title),
        'content': "%s %s"%(unicode(o.description),
            unicode(getattr(o, 'content', ''))),
        }


class ObjectBrowser(drink.Page):
    mime = "search"

    doc = "A very basic object finder"

    classes = {}

    hidden_class = True # TODO: add non-hidden finder that is not whoosh related but more
                        # like the old "Dumb" indexer, with local (but recursive) lookup
                        # OR : "find" method on any page, with optional recursive attr

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.lastlog = {}

    def _add_object(self, objs):
        w = indexer.writer()
        if hasattr(objs, 'title'):
            objs = [objs]

        for obj in objs:
            w.add_document(**extract_obj(obj))

        w.commit()

    def _del_object(self, obj):
        w = indexer.writer()
        w.delete_by_term("path", obj.path)
        w.commit()

    def _update_object(self, obj):
        w = indexer.writer()
        w.update_document(**extract_obj(obj))
        w.commit()

    def query(self, pattern=None, query_type=None):
        pattern = pattern if pattern != None else drink.request.forms.get('pattern')
        query_type = query_type if query_type != None else drink.request.forms.get('qtype')
        searcher = indexer.searcher()
        auth = drink.request.identity

        if query_type == 'fast':
            pat = pattern.strip()
        else:
            pat = 'title:%(p)s OR content:%(p)s'%dict(p=pattern.strip())

        res = searcher.search(qparser.parse(unicode(pat)))

        items = []
        html = ['<ul>']
        root = drink.db.db
        for item in res:
            obj = drink.get_object(root, item['path'])
            if 'r' in auth.access(obj):
                items.append(obj)
                html.append('<li><a href="%(path)s">%(title)s</a></li>'%item)
        html.append('</ul>')
        self.lastlog[auth.id] = (pat, items)
        drink.transaction.commit()
        return drink.template('main.html', obj=self, html='\n'.join(html),
                    authenticated=auth, classes=self.classes)

    def view(self):
        auth = drink.request.identity

        if auth.id in self.lastlog:
            pat, items = self.lastlog[auth.id]
        else:
            pat = ''
            items = None

        form = ['<form class="query_form" id="query_form" action="query" method="post">',
            drink.types.Text('Look for').html('pattern', pat),
            drink.types.CheckboxSet("Search type", values=['fast']).html('qtype', ['fast']),
            '<input class="submit" type="submit" value="GO!"/></form>']
        if items:
            form.append('<h2>Last search</h2>')

            form.extend('<li><a href="%s">%s</a></li>'%(i.path, i.title) for i in items)

        return drink.template('main.html', obj=self, html='\n'.join(form), authenticated=auth, classes=self.classes)

init()

exported = {"Finder": ObjectBrowser}

