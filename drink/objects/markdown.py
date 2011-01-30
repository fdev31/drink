from __future__ import absolute_import
import transaction
from .generic import Page, TextArea, Text
from drink import request, template, authenticated

from markdown import markdown

class MarkdownPage(Page):
    content = "[Edit me](edit)"

    mime = "markdown"

    doc = "A markdown rendered page"

    editable_fields = {
        'content': TextArea(),
        'mime': Text(),
    }

    def view(self):
        html = markdown(self.content)
        return template('main.html', obj=self,
             html=html, authenticated=authenticated(),
             classes=exported,
             )

exported = {'Markdown Page': MarkdownPage}