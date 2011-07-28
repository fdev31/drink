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
        'title': o.title,
        'tags': unicode(o.mime),
        'content': o.indexable,
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
        drink.response.content_type = "text/plain; charset=utf-8"

        w = indexer.writer()
        w.delete_by_query(qparser.parse(u"*"))
        w.commit()
        indexer.optimize()

        objs = [drink.db.db['pages']]
        for obj in objs:
            yield (u"%s\n"%obj.title).encode('utf-8')
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

    # TODO: make a js-friendly function & use it
    def query(self, pattern=None, query_type=None, page=None):
        pattern = pattern if pattern != None else drink.request.params.get('pattern').decode('utf-8')
        query_type = query_type if query_type != None else drink.request.params.get('qtype')
        page_nr = int(page if page else drink.request.params.get('page', 1))

        try:
            searcher = indexer.searcher()
        except IOError:
            reset()
            self.rebuild()
            searcher = indexer.searcher()

        auth = drink.request.identity

        pat = pattern.strip()
        qpat = qparser.parse(pat)
        res = searcher.search_page(qpat, page_nr, pagelen=10)
        sentence_frag = highlight.SentenceFragmenter()
        whole_frag = highlight.WholeFragmenter()

        items = []
        html = ['<ul class="results">']
        root = drink.db.db
        for item in res:
            obj = drink.get_object(root, quote(item['path'].encode('utf-8')), no_raise=True)
            if obj == None:
                continue
            if 'r' in auth.access(obj):
                items.append(obj)
                title =  item.highlights('title', fragmenter=whole_frag) or item['title']
                hli =  item.highlights('content', fragmenter=sentence_frag)
                html.append('<li><a href="%s">%s</a></li>'%(item['path'], title))
                if hli:
                    html.append('<a href="%s"><div class="minipage">%s</div></a>'%(item['path'],hli.replace('\n', '<br/>')))
        if res.pagecount:
            html.append('</ul><br/>pages:&nbsp;')
            for page in xrange(1, 1+res.pagecount):
                if page == page_nr:
                    html.append( '<span class="page_nr_cur">%s</span>'%page )
                else:
                    html.append( '<a href="%s"><span class="page_nr">%s</span></a>'%("%squery?pattern=%s&qtype=%s&page=%s"%(self.path, pattern, query_type, page), page ) )
        else:
            #corr = searcher.correct_query(qparser, pat)
            #html.append('</ul><br/>No matching documents!<br/>Did you mean <a href="%squery?pattern=%s&qtype=%s">%s</a>'%(self.path, corr.string, query_type, corr.string))
            html.append('</ul><br/>No matching documents!')
        self.lastlog[auth.id] = (pat, items)
        drink.transaction.commit()
        return drink.template('main.html', obj=self, html='\n'.join(html),
                    authenticated=auth, classes=self.classes)

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

            form.extend('<li><a href="%s">%s</a></li>'%(i.path, i.title) for i in items)

        return drink.template('main.html', obj=self, html='\n'.join(form), authenticated=auth, classes=self.classes)

init()

exported = {"Finder": ObjectBrowser}

