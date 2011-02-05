import drink
from . import classes
import transaction


class User(drink.Model):

    mime = "user"

    doc = "User object"

    password = ''

    classes = {}

    groups = set()

    editable_fields = {
        'id': drink.types.Id(),
        'doc': drink.types.Text(),
        'name': drink.types.Text(),
        'surname': drink.types.Text(),
        'password': drink.types.Password(),
        'groups': drink.types.GroupCheckBoxes(),
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


class UserList(drink.ListPage):
    doc = "Users folder"
    mime = "group"

    classes = {'User': User}


class Group(drink.Page):

    mime = "group"

    doc = "A group"

    name = "unnamed group"

    classes = {}

    editable_fields = {}

    def view(self):
        return 'keep out'


class GroupList(drink.ListPage):
    doc = "Groups"
    mime = "group"

    classes = {'Group': Group}


exported = {}
