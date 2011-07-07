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
            Schema(
                path=ID(stored=True, unique=True),
                title=TEXT(stored=True),
                tags=KEYWORD(scorable=True),
                content=TEXT(stored=True),
                )
        )

    qparser = QueryParser("title", schema=indexer.schema)

def reset():
    import shutil
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    init()

def extract_obj(o):
    return {
        'path': unicode(o.path),
        'title': unicode(o.title),
        'tags': unicode(o.mime),
        'content': unicode(o.content) if hasattr(o, 'content') else "%s %s"%(unicode(o.description), unicode(o.description)),
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

    def rebuild(self):
        drink.response.content_type = "text/plain"
        objs = [drink.db.db['pages']]
        for obj in objs:
            yield "%s\n"%obj.title
            c = obj.values()
            if c:
                objs.extend(c)
        self._add_object(objs)
        yield "-eof-"

    def _add_object(self, objs):
        w = indexer.writer()
        if not isinstance(objs, (list, tuple)):
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

    def query(self, pattern=None, query_type=None, page=None):
        pattern = pattern if pattern != None else drink.request.params.get('pattern')
        query_type = query_type if query_type != None else drink.request.params.get('qtype')
        page_nr = int(page if page else drink.request.params.get('page', 1))

        try:
            searcher = indexer.searcher()
        except IOError:
            reset()
            self.rebuild()
            searcher = indexer.searcher()

        auth = drink.request.identity

        if query_type == 'fast':
            pat = pattern.strip()
        else:
            pat = 'title:%(p)s OR content:%(p)s'%dict(p=pattern.strip())

        res = searcher.search_page(qparser.parse(unicode(pat)), page_nr)

        items = []
        html = ['<ul>']
        root = drink.db.db
        for item in res:
            obj = drink.get_object(root, item['path'].encode('utf-8'))
            if 'r' in auth.access(obj):
                items.append(obj)
                html.append('<li><a href="%(path)s">%(title)s</a></li>'%item)
                hli =  item.highlights('content')
                if hli:
                    html.append('<a href="%s"><div class="minipage">%s</div></a>'%(item['path'],hli.replace('\n', '<br/>')))
        html.append('</ul><br/>pages:&nbsp;')
        for page in xrange(1, 1+res.pagecount):
            if page == page_nr:
                html.append( '<span class="page_nr_cur">%s</span>'%page )
            else:
                html.append( '<a href="%s"><span class="page_nr">%s</span></a>'%("%squery?pattern=%s&qtype=%s&page=%s"%(self.path, pattern, query_type, page), page ) )

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

