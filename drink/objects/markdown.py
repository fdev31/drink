from __future__ import absolute_import
import drink
from markdown import Markdown

DEFAULT_CONTENT = """
<!- hehe, you can add html tags directly too: -->

Main title of the document
==========================

Getting started
---------------

You can add your content here... [Edit me](edit)

Get a quick overview of the syntax [here](http://daringfireball.net/projects/markdown/basics)

or something more complete [here](http://daringfireball.net/projects/markdown/syntax).

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


class MarkdownPage(drink.Page):
    content = DEFAULT_CONTENT

    mime = "markdown"

    description = "A markdown rendered page"

    js = drink.Page.js + ['/static/markitup/jquery.markitup.js',
        '/static/markitup/sets/markdown/set.js']

    css = drink.Page.css + ['/static/markitup/sets/markdown/style.css',
     '/static/markitup/skins/markitup/style.css']

    markup_name = ''

    _template = r'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<link rel="stylesheet" type="text/css" href="/static/page.css" />
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Drink! preview template</title>
</head>
<body>
%s
</body>
</html>
'''

    editable_fields = drink.Page.editable_fields.copy()
    editable_fields.update({
        'content': MarkdownEditor("Content"),
        'markup_name': drink.types.Text('[[WikiLink]] name'),
        'mime': drink.types.Text(),
    })

    def __init__(self, name, rootpath=None):
        drink.Page.__init__(self, name, rootpath)
        self.markup_name = name

    def _wikify(self, label, base, end):
        cache = getattr(self, '_wikilinks', {})
        labels = self.keys()
        if label in cache:
            real_id = cache[label]
            labels.remove(real_id)
            labels.insert(0, real_id)

        for lbl in labels:
            if label == getattr(self[lbl], 'markup_name', None):
                ret = '%s%s/view'%(base, lbl)
                break
        else:
            ret = '%sadd?name=%s&class=%s'%(base, label, _title)
            lbl = None

        if lbl:
            cache[label] = lbl

        self._wikilinks = cache
        return ret

    def process(self, data=None):
        if not hasattr(self, '_v_wikifier_cache'):
            self._v_wikifier_cache = Markdown(
            extensions = ['tables', 'wikilinks', 'fenced_code',
            'toc', 'def_list', 'codehilite(force_linenos=True)'],
            extension_configs = {
                "codehilite":
                     ("force_linenos", True),
                "wikilinks":
                    [("base_url", self.path), ('build_url', self._wikify)],
                }
            )

        return self._template % self._v_wikifier_cache.convert(data or drink.request.params.get('data'))

    def view(self):

        html = self.process(self.content)

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.request.identity,
             # do not include js code, or css code, it's only for editing
             classes=self.classes,
             )

    def _upload(self, obj):
        self.content = obj.file.read()

_title = 'Web page (markdown)'

exported = {_title: MarkdownPage}
drink.Page.upload_map['md'] = _title

