import drink
from . import classes
import transaction
from hashlib import md5


class User(drink.Model):

    mime = "user"

    doc = "User object"

    password = ''

    email = ''

    classes = {}

    groups = set()

    default_read_groups = set()

    default_write_groups = set()

    admin_fields = drink.Model.admin_fields.copy()

    admin_fields.update( {
        'doc': drink.types.Text(),
        'groups': drink.types.GroupCheckBoxes(),
    } )
    owner_fields = {
    # FIXME: Don't look ordered by group !
        'title': drink.types.Text('Nickname', group='0'),
        'name': drink.types.Text(group='1'),
        'surname': drink.types.Text(group='2'),
        'email': drink.types.Text(group='3'),
        'password': drink.types.Password(group='4'),
        'default_read_groups': drink.types.GroupCheckBoxes('Default readers Groups', group='x_permissions'),
        'default_write_groups': drink.types.GroupCheckBoxes('Default writers Groups', group='x_permissions'),
    }

    editable_fields = {
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
        group_list._add(name, Group, {}, {})
        self.groups.add(group_list[name])
        transaction.commit()

    def view(self):
        drink.rdr(self.path+'edit')

    def edit(self):
        r = drink.Model._edit(self)
        uid = md5(self.email).hexdigest()
        self.mime = 'http://www.gravatar.com/avatar/%s?s=32'%uid
        return drink.Model.edit(self, resume=r)

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
