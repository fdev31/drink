import drink
from . import classes
import transaction
from hashlib import md5


class User(drink.Page):

    mime = "user"

    description = "User object"

    password = ''

    email = ''

    classes = {}

    groups = set()

    default_read_groups = set()

    default_write_groups = set()

    admin_fields = drink.Page.admin_fields.copy()

    admin_fields.update( {
        'description': drink.types.Text(),
        'groups': drink.types.GroupCheckBoxes(),
        'read_groups':
            drink.types.GroupCheckBoxes("Read-enabled groups", group="x_permissions"),
        'min_rights':
            drink.types.Text("Every user's permissions (wrta)", group="x_permissions"),
        'write_groups':
            drink.types.GroupCheckBoxes("Write-enabled groups", group="x_permissions")
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

    default_action = "edit"

    def __init__(self, name, rootpath):
        drink.Page.__init__(self, name, rootpath)
        name = self.id
        self.phones = {}
        self.groups = set()
        self.name = "no name"
        self.surname = "no surname"
        new_grp = drink.db.db['groups']._add(name, Group, {}, {})
        self.groups.add(new_grp.id)
        self.write_groups.add(new_grp.id)
        self.owner = self
        new_grp.owner = self
        transaction.commit()

    def edit(self):
        r = drink.Page._edit(self)
        uid = md5(self.email).hexdigest()
        self.mime = 'http://www.gravatar.com/avatar/%s?s=32'%uid
        return drink.Page.edit(self, resume=r)


class UserList(drink.ListPage):
    description = "Users folder"
    mime = "group"

    classes = {'User': User}


class Group(drink.Page):

    mime = "group"

    description = "A group"

    name = "unnamed group"

    classes = {}

    editable_fields = {}

    def view(self):
        return "Hi! I'm the %r(%r) group :)"%(self.name, self.id)


class GroupList(drink.ListPage):
    description = "Groups"
    mime = "groups"

    classes = {'Group': Group}


exported = {}
