import drink
from . import classes

class UserList(drink.Page):
    doc = "Users folder"
    mime = "group"

    def view(self):
        return drink.template('list.html', obj=self, classes=classes, authenticated=drink.authenticated())


class User(drink.Model):

    mime = "user"

    doc = "User object"

    password = ''

    editable_fields = {
        'id': drink.Id(),
        'age': drink.Text(),
        'doc': drink.Text(),
        'name': drink.Text(),
        'surname': drink.Text(),
        'password': drink.Password(),
    }

    def __init__(self):
        self.age = None
        self.phones = {}
        self.name = "no name"
        self.surname = "no surname"

    @property
    def title(self):
        return self.id

exported = {'Users folder': UserList, "User": User}
