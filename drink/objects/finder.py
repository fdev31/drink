from __future__ import absolute_import

import os
import drink
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser

INDEX_DIR = os.path.join(drink.DB_PATH, 'whoosh')
if os.path.exists(INDEX_DIR):
    indexer = open_dir(INDEX_DIR)
else:
    os.mkdir(INDEX_DIR)
    indexer = create_in(
        INDEX_DIR,
        Schema(path=ID(stored=True, unique=True), title=TEXT(stored=True), content=TEXT)
    )

qparser = QueryParser("title", schema=indexer.schema)

class ObjectBrowser(drink.Page):
    mime = "search"

    doc = "A very basic object finder"

    classes = {}

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.lastlog = {}

    def _add_object(self, objs):
        w = indexer.writer()
        if hasattr(objs, 'title'):
            objs = [objs]

        for obj in objs:
            w.add_document(path=unicode(obj.path), title=unicode(obj.title), content=unicode(obj.content))

        w.commit()

    def _update_object(self, obj):
        w = indexer.writer()
        w.update_document(path=unicode(obj.path), title=unicode(obj.title), content=unicode(obj.content))
        w.commit()

    def query(self, full=False):
        pat = drink.request.forms.get('pattern')
        searcher = indexer.searcher()
        auth = drink.request.identity

        q = qparser.parse(unicode(pat))
        '''
        if full:
            q = Or([Term("content", pat), Term("title", pat)])
        else:
            q = Or([Term("title", pat)])
        '''

        res = searcher.search(q)
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
        return drink.template('main.html', obj=self, html='\n'.join(html), authenticated=auth, classes=self.classes)

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
