from drink.objects.generic import Page, Text, Model, Id, Password
from drink import authenticated, template
from . import classes

class UserList(Page):
    doc = "Users folder"
    mime = "group"

    def view(self):
        return template('list.html', obj=self, classes=classes, authenticated=authenticated())


class User(Model):

    mime = "user"

    doc = "User object"

    password = ''

    editable_fields = {
        'id': Id(),
        'age': Text(),
        'doc': Text(),
        'name': Text(),
        'surname': Text(),
        'password': Password(),
    }

    def __init__(self):
        self.age = None
        self.phones = {}
        self.name = "no name"
        self.surname = "no surname"

    @property
    def title(self):
        return self.id

exported = {'User folder': UserList, "User": User}
