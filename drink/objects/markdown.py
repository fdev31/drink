from __future__ import absolute_import
import transaction
import drink

from markdown import markdown

class MarkdownPage(drink.Page):
    content = "[Edit me](edit)"

    mime = "markdown"

    doc = "A markdown rendered page"

    editable_fields = {
        'content': drink.TextArea(),
        'mime': drink.Text(),
    }

    def view(self):

        html = markdown(self.content)

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.authenticated(),
             classes=exported,
             )

exported = {'Markdown Page': MarkdownPage}