import drink
from hashlib import md5


class User(drink.Page):

    drink_name = None

    mime = "user"

    description = u"User object"

    password = ''

    email = ''

    classes = {}

    groups = set()

    default_action = "edit"

    default_read_groups = set()

    default_write_groups = set()

    editable_fields = {}

    owner_fields = {
    # FIXME: Don't look ordered by group !
        'title': drink.Page.editable_fields['title'],
        'name': drink.types.Text(group='1'),
        'surname': drink.types.Text(group='2'),
        'email': drink.types.Text(group='3'),
        'password': drink.types.Password(group='4'),
        'default_read_groups': drink.types.GroupCheckBoxes("Users that can read your documents by default", group='xx_permissions'),
        'default_write_groups': drink.types.GroupCheckBoxes("Groups that can edit your documents by default", group='xx_permissions'),
    }
    owner_fields['title'].caption = 'Nickname'

    admin_fields = drink.Page.owner_fields.copy()
    del admin_fields['default_action']
    admin_fields['description'] = drink.Page.editable_fields['description']

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
        drink.transaction.commit()

    @property
    def html(self):
        return '''
        <h2>%(id)s</h2>
        <strong>Name</strong>: %(name)s
        <strong>Surname</strong>: %(surname)s
        <strong>Phones</strong>: %(phones)r
        '''%self.__dict__

    def edit(self):
        r = drink.Page._edit(self)
        uid = md5(self.email).hexdigest()
        self.mime = 'http://www.gravatar.com/avatar/%s?s=32'%uid
        return drink.Page.edit(self, resume=r)


class UserList(drink.ListPage):

    drink_name = None

    description = u"Users folder"

    mime = "group"

    classes = {'User': User}


class Group(drink.Page):

    drink_name = None

    mime = "group"

    description = "A group"

    name = "unnamed group"

    classes = {}

    editable_fields = {}

    def view(self):
        return "Hi! I'm the %r(%r) group :)"%(self.name, self.id)


class GroupList(drink.ListPage):

    drink_name = None

    description = u"Groups"

    mime = "groups"

    classes = {'Group': Group}
