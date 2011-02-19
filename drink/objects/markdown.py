from __future__ import absolute_import
import drink
from markdown import markdown

def mark_it_down(txt):
    return markdown(txt, ['tables', 'fenced_code', 'codehilite(force_linenos=True)'])

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
    content = "# Your document title\n\n[Edit me](edit)"

    mime = "markdown"

    description = "A markdown rendered page"

    js = ['/static/markitup/jquery.markitup.js',
        '/static/markitup/sets/markdown/set.js']

    css = ['/static/markitup/skins/markitup/style.css',
        '/static/markitup/sets/markdown/style.css']

    editable_fields = drink.Page.editable_fields.copy()
    editable_fields.update({
        'content': MarkdownEditor("Content"),
        'mime': drink.types.Text(),
    })

    def process(self):
        return mark_it_down(drink.request.forms.get('data'))

    def view(self):

        html = mark_it_down(self.content)

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.request.identity,
             # do not include js code, or css code, it's only for editing
             classes=self.classes,
             )

exported = {'Web page (markdown)': MarkdownPage}

