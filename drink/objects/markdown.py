from __future__ import absolute_import
import transaction
import drink

from markdown import markdown

class MarkdownPage(drink.Page):
    content = "[Edit me](edit)"

    mime = "markdown"

    doc = "A markdown rendered page"

    editable_fields = drink.Page.editable_fields.copy()
    editable_fields.update({
        'content': drink.TextArea("Content"),
        'mime': drink.Text(),
    })

    def view(self):

        html = markdown(self.content)

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.request.identity,
             classes=self.classes,
             )

exported = {'Markdown page': MarkdownPage}