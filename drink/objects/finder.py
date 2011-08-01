from __future__ import absolute_import
# http://packages.python.org/Whoosh/querylang.html
# http://packages.python.org/Whoosh/parsing.html

import os
import drink
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh import highlight
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import FuzzyTerm
from urllib import quote

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

    qparser = MultifieldParser(["title", "content"],
            schema=indexer.schema,
            group=OrGroup,
            termclass=FuzzyTerm,
            )

def reset():
    import shutil
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    init()

def extract_obj(o):
    return {
        'path': o.path,
        'title': unicode(o.title),
        'tags': unicode(o.mime),
        'content': o.indexable,
        }


class ObjectBrowser(drink.Page):
    mime = "search"

    doc = u"A very basic object finder"

    classes = {}

    hidden_class = True # TODO: add non-hidden finder that is not whoosh related but more
                        # like the old "Dumb" indexer, with local (but recursive) lookup
                        # OR : "find" method on any page, with optional recursive attr

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        self.lastlog = {}

    def rebuild(self):
        drink.response.content_type = "text/plain; charset=utf-8"

        w = indexer.writer()
        w.delete_by_query(qparser.parse(u"*"))
        w.commit()
        indexer.optimize()

        objs = [drink.db.db['pages']]
        for obj in objs:
            yield (u"%s\n"%obj.title).encode('utf-8')
            c = obj.values()
            if c and not getattr(obj, '_no_scan', False):
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

    def _query(self, pattern=None, query_type=None, page_nr=1, results=10):
        # Fire up searcher
        try:
            searcher = indexer.searcher()
        except IOError:
            reset()
            self.rebuild()
            searcher = indexer.searcher()


        qpat = qparser.parse(pattern.strip())
        res = searcher.search_page(qpat, page_nr, pagelen=results)

        items = []
        result = []
        auth = drink.request.identity
        sentence_frag = highlight.SentenceFragmenter()
        whole_frag = highlight.WholeFragmenter()
        root = drink.db.db

        for item in res:
            obj = drink.get_object(root, quote(item['path'].encode('utf-8')), no_raise=True)
            if obj == None:
                # TODO: add a log here
                continue

            if 'r' in auth.access(obj):
                match = {'path': item['path'], 'item': item['path']}
                items.append(obj)
                title =  item.highlights('title', fragmenter=whole_frag) or item['title']
                match['hi_title'] = title
                match['hi'] =  item.highlights('content', fragmenter=sentence_frag)
                result.append(match)
        return (res.pagecount, result)

    # TODO: Use self.path to answer
    def query(self):
        # parse Query parameters
        pattern =  drink.request.params.get('pattern')
        query_type = drink.request.params.get('qtype')
        page_nr = int(drink.request.params.get('page', 1))
        results = int(drink.request.params.get('results', 10))
        fmt = drink.request.params.get('fmt', 'html')
        if pattern:
            pattern = pattern.decode('utf-8')
        else:
            return 'Give me a pattern please !'

        # Let's compute

        pages, matches = self._query(pattern, query_type, page_nr, results)

        if fmt == 'js':
            return dict(pages=pages, items=matches)

        # make html
        html = ['<ul class="results">']
        for item in matches:
            if isinstance(item, basestring):
                continue
            html.append('<li><a href="%(path)s">%(hi_title)s</a></li>'%item)
            if item.get('hi', None):
                html.append('<a href="%s"><div class="minipage">%s</div></a>'%(item['path'], item['hi'].replace('\n', '<br/>')))

        if pages > 1:
            html.append('</ul><br/>pages:&nbsp;')

            for page in xrange(1, 1+pages):
                if page == page_nr:
                    html.append( '<span class="page_nr_cur">%s</span>'%page )
                else:
                    html.append( '<a href="%s"><span class="page_nr">%s</span></a>'%("%squery?pattern=%s&qtype=%s&page=%s"%(self.path, pattern, query_type, page), page ) )
        elif pages == 1:
            html.append('</ul>')
        elif not pages:
            html.append('</ul><br/>No matching documents!')

        # save log
        self.lastlog[drink.request.identity.id] = (pattern, matches)

        # render
        return drink.template('main.html', obj=self, html='\n'.join(html),
                    authenticated=drink.request.identity, classes=self.classes, embed=False)

    # TODO: Change that to Javascript code, use a refactored `make_li` to create new items
    def view(self):
        auth = drink.request.identity

        if auth.id in self.lastlog:
            pat, items = self.lastlog[auth.id]
        else:
            pat = ''
            items = None

        form = ['<form class="query_form" id="query_form" action="query" method="post">',
            drink.types.Text('Look for').html('pattern', pat),
#            drink.types.CheckboxSet("Search type", values=['fast']).html('qtype', ['fast']),
            '<input class="submit" type="submit" value="GO!"/></form>']
        form.append('<a href="http://packages.python.org/Whoosh/querylang.html">Overview of language (fields: path, title, content, tags)</a>')
        if items:
            form.append('<h2>Last search</h2>')

            form.extend('<li><a href="%(path)s">%(title)s</a></li>'%i for i in items)

        return drink.template('main.html', obj=self, html='\n'.join(form), authenticated=auth, classes=self.classes, embed=False)

init()

exported = {"Finder": ObjectBrowser}

