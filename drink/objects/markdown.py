from __future__ import absolute_import
import transaction
import drink

from markdown import markdown

class MarkdownEditor(drink.types._Editable):
    def html(self, caption, group):
        return drink.types._Editable.html(self, caption, group, '''
<script type="text/javascript" >
   $(document).ready(function() {
      $("#%(id)s").markItUp(mySettings);
   });
</script>
<br/>
<textarea id="%(id)s" name="%(name)s" cols="80" rows="25">%(value)s</textarea>
    ''')

class MarkdownPage(drink.Page):
    content = "# You'r document title\n\n[Edit me](edit)"

    mime = "markdown"

    doc = "A markdown rendered page"

    js = ['/static/markitup/jquery.markitup.js', '/static/markitup/sets/markdown/set.js']

    css = ['/static/markitup/skins/markitup/style.css', '/static/markitup/sets/markdown/style.css']

    editable_fields = drink.Page.editable_fields.copy()
    editable_fields.update({
        'content': MarkdownEditor("Content"),
        'mime': drink.types.Text(),
    })

    def process(self):
        return markdown(drink.request.forms.get('data'))

    def view(self):

        html = markdown(self.content)

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.request.identity,
             css=self.css,
             classes=self.classes,
             )

exported = {'Web page (markdown)': MarkdownPage}