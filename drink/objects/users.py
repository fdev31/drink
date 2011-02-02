import drink
from . import classes

class UserList(drink.Page):
    doc = "Users folder"
    mime = "group"

    def view(self):
        return drink.template('list.html', obj=self, classes={'User': User}, authenticated=drink.authenticated())

class GroupList(drink.Page):
    doc = "Groups"
    mime = "group"

    def view(self):
        return drink.template('list.html', obj=self, classes={'Group': Group}, authenticated=drink.authenticated())


class User(drink.Model):

    mime = "user"

    doc = "User object"

    password = ''

    classes = {}

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

    def view(self):
        drink.rdr(self.path+'edit')

class Group(drink.Page):

    mime = "group"

    doc = "A group"

    name = "unnamed group"

    gid = 0

    classes = {}

    editable_fields = {'gid': drink.Int(), 'id': drink.Id()}

    def view(self):
        drink.rdr(self.path+'edit')

# Model.owner = User
# Model.anonymous = 'ro' or 'rw' or None
# Model.ro_groups = set(gid1, gid2, gid3, ...)
# Model.rw_groups = set(gid1, gid2, gid3, ...)

exported = {'Users folder': UserList, "User": User}
