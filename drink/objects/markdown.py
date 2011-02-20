from __future__ import absolute_import
import drink
from markdown import Markdown

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

wikifier_cache = {}

class MarkdownPage(drink.Page):
    content = "# Your document title\n\n[Edit me](edit)"

    mime = "markdown"

    description = "A markdown rendered page"

    js = drink.Page.js + ['/static/markitup/jquery.markitup.js',
        '/static/markitup/sets/markdown/set.js']

    css = drink.Page.css + ['/static/markitup/sets/markdown/style.css', '/static/markitup/skins/markitup/style.css']

    markup_name = ''

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
        for lbl in self:
            if label == self[lbl].markup_name:
                return '%s%s/view'%(base, lbl)
        return '%sadd?name=%s&class=%s'%(base, label, _title)

    def process(self, data=None):
        md = wikifier_cache.get(self.path, None) or Markdown(
            extensions = ['tables', 'wikilinks', 'fenced_code', 'codehilite(force_linenos=True)'],
            extension_configs = {
            "codehilite":
                 ("force_linenos", True),
            "wikilinks":
                [("base_url", self.path), ('build_url', self._wikify)],
            },
        )
        wikifier_cache[self.path] = md

        return md.convert(data or drink.request.forms.get('data'))

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

