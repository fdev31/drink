from __future__ import absolute_import
import drink
import logging
log = logging.getLogger('spreadsheet')

class SpreadSheet(drink.Page):

    drink_name = 'SpreadSheet'

    mime = u"markdown"

    default_action = "view"

    '''
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
    '''

    js = drink.Page.js + ['/static/js/raphael-min.js',
            '/static/js/g.raphael-min.js',
            '/static/js/parser.js',
            '/static/js/jquery.sheet.min.js',
            '/static/js/jquery.colorPicker.min.js',
    '''
    $(document).ready(function(){
        $('.spreadsheet').sheet({
            title: "foinfoin",
            urlGet: "/static/sheet.doc.html",
            urlMenu: "/static/sheet.menu.html",
            urlSave: "",
            autoFiller: true,
            });
    });
    ''']

    html = '<div class="spreadsheet" />'

    css = [
            '/static/css/jquery.sheet.css',
            '/static/css/jquery.colorPicker.css',
            ] + drink.Page.css
