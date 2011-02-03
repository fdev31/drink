import drink
from . import classes
import transaction

class UserList(drink.Page):
    doc = "Users folder"
    mime = "group"

    def view(self):
        return drink.template('list.html', obj=self, classes={'User': User}, authenticated=drink.request.identity)

class GroupList(drink.Page):
    doc = "Groups"
    mime = "group"

    def view(self):
        return drink.template('list.html', obj=self, classes={'Group': Group}, authenticated=drink.request.identity)


class User(drink.Model):

    mime = "user"

    doc = "User object"

    password = ''

    classes = {}

    groups = set()

    editable_fields = {
        'id': drink.Id(),
        'doc': drink.Text(),
        'name': drink.Text(),
        'surname': drink.Text(),
        'password': drink.Password(),
        'groups': drink.GroupListArea(),
    }

    @property
    def owner(self):
        return self

    def __init__(self, name, rootpath):
        drink.Model.__init__(self, name, rootpath)
        self.phones = {}
        self.groups = set()
        self.name = "no name"
        self.surname = "no surname"
        group_list = drink.get_object(drink.db, 'groups')
        group_list._add(name=name, cls=Group)
        self.groups.add(group_list[name])
        transaction.commit()

    @property
    def title(self):
        return self.id

    def view(self):
        drink.rdr(self.path+'edit')

class Group(drink.Page):

    mime = "group"

    doc = "A group"

    name = "unnamed group"

    classes = {}

    editable_fields = {}

    def view(self):
        return 'keep out'
exported = {}