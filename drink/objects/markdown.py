from __future__ import absolute_import
import os
import drink
import shutil
import logging
import tempfile
import datetime
from markdown import Markdown
log = logging.getLogger('markdown')
try:
    import landslide.main
    from landslide import generator
    landslide = True
except ImportError:
    log.warning('Landslide is not installed: disabling slideshow feature')
    landslide = False

DEFAULT_CONTENT = u"""
# Untitled page

<img style="float: left; margin: 1ex" src="/static/mime/note.png" />

You can add your content here... [edit me!](edit)


---

Markdown syntax
: [basic](http://daringfireball.net/projects/markdown/basics) or [full](http://daringfireball.net/projects/markdown/syntax)

"""

class MarkdownEditor(drink.types._Editable):
    def html(self, caption, group):
        return drink.types._Editable.html(self, caption, group, '''
<script type="text/javascript" >
   $(document).ready(function() {
      $("#%(id)s").markItUp(mySettings);
   });
</script>
<textarea id="%(id)s" name="%(name)s" cols="80" rows="25">%(value)s</textarea>
    ''')


class MarkdownPage(drink.ListPage):
    content = DEFAULT_CONTENT

    drink_name = 'Web page (markdown)'

    mime = u"markdown"

    default_action = "view"

    creation_date = ''

    sort_order = 'date'

    forced_order = []

    markup_name = ''

    subpages_blog = False

    editable_fields = drink.ListPage.editable_fields.copy()

    editable_fields.update({
        'sort_order': drink.types.Choice('Sort blog entries by', {
                'default listing order': '',
                'creation date': 'date',
                'rating': 'rating',
                'title\'s alphabetical order': 'title',
            }),
        'creation_date': drink.types.Date("Creation date"),
        'content': MarkdownEditor("Content"),
        'subpages_blog': drink.types.BoolOption("Include children web pages like a blog"),
        'markup_name': drink.types.Text('[[WikiLink]] name'),
        'mime': drink.types.Mime(),
    })

    editable_fields.pop('description')

    js = drink.ListPage.js + ['/static/markitup/jquery.markitup.js',
        '/static/markitup/sets/markdown/set.js',
    '''
    $(document).ready(function(){
        m = new MarkDown();
        m.load_page();
        add_hook_add_item(function() {m.load_page});
    });
    ''']

    css = drink.ListPage.css + ['/static/markitup/sets/markdown/style.css',
     '/static/markitup/skins/markitup/style.css']

    #    _template = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    #<html xmlns="http://www.w3.org/1999/xhtml">
    #<head>
    #<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    #<title>Drink! preview template</title>
    #</head>
    #<body>
    #%s
    #</body>
    #</html>
    #'''

    _v_slide_cooked = ''
    _v_view_cooked = ''

    _actions = drink.ListPage._actions + []
    if landslide:
        _actions.append(dict(title="Slide!", action="slide", perm="r", icon="view"))

    def __init__(self, name, rootpath=None):
        drink.ListPage.__init__(self, name, rootpath)
        self.markup_name = name
        self.date = datetime.date.today()

    @property
    def description(self):
        return (l for l in self.content.split('\n') if l.strip()).next()

    def slide(self):
        if not self._v_slide_cooked:
            workdir = tempfile.mkdtemp(suffix=".drink-mdown")
            in_f = os.path.join(workdir, 'in.md')
            out_f = os.path.join(workdir, 'out.html')
            open(in_f, 'w').write(self.content.encode('utf-8'))
            try:
                g = generator.Generator(in_f, destination_file=out_f, embed=True)
                g.execute()
                self._v_slide_cooked = open(out_f).read()
            except Exception, e:
                log.error("Slide Error: %r", e)
            finally:
                shutil.rmtree(workdir)
        return self._v_slide_cooked

    def _wikify(self, label, base, end):
        cache = getattr(self, '_wikilinks', {})
        labels = self.keys()
        if label in cache:
            real_id = cache[label]
            try:
                labels.remove(real_id)
            except ValueError:
                cache.pop(label)
            labels.insert(0, real_id)

        for lbl in labels:
            if label == getattr(self[lbl], 'markup_name', None):
                ret = '%s%s/view'%(base, lbl)
                break
        else:
            ret = '%sadd?name=%s&class=%s'%(base, label, self.drink_name)
            lbl = None

        if lbl:
            cache[label] = lbl

        self._wikilinks = cache
        return ret

    html = '''<div id="markdown" class="editable" edit_type="process"></div>'''

    def blog_content(self):
        dn = self.drink_name
        items = [i for i in self.itervalues() if i.drink_name == dn]
        if self.sort_order == 'date':
            sort_key = lambda x: x.creation_date
        elif self.sort_order == 'title':
            sort_key = lambda x: x.title
        elif self.sort_order == 'rating':
            sort_key = lambda x: x.rate()['rating']
        else:
            sort_key = None

        if sort_key:
            items.sort(key=sort_key)

        htmls = [ u'<h1>%s</h1><div class="blog_entries">'%self.title ]
        htmls.extend(u'<div class="blog_entry row" >%s</div>'%(i.process()) for i in reversed(items))
        htmls.append(u'</div>')
        return u'\n'.join(htmls)

    @property
    def indexable(self):
        return self.content

    def _add(self, *args, **kw):
        new_obj = drink.ListPage._add(self, *args, **kw)
        self.content += (u"\n* link to [%s](%s/)"%(
            new_obj.title, new_obj.id))
        return new_obj

    def edit(self, *a, **kw):
        self._v_slide_cooked = ''
        self._v_view_cooked = ''
        return drink.ListPage.edit(self, *a, **kw)

    def process(self, data=None):
        data = data or drink.request.params.get('data')
        log.debug(data)
        use_cache = bool(data)
        if not use_cache or not self._v_view_cooked:
            if not hasattr(self, '_v_wikifier_cache'):
                self._v_wikifier_cache = Markdown(
                extensions = ['tables', 'codehilite', 'wikilinks',
                'toc', 'def_list'],
                #                , 'fenced_code'],
                extension_configs = {
                    "wikilinks":
                        [("base_url", self.path), ('build_url', self._wikify)],
                    }
                )

            data = self._v_wikifier_cache.convert(drink.omni(data or self.content))

            if use_cache:
                self._v_view_cooked = data
            else:
                return data

        return self._v_view_cooked

    def _upload(self, obj):
        self.content = drink.omni(obj.file.read())

drink.add_upload_handler(['md', 'txt'], MarkdownPage.drink_name)
