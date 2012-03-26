import drink
from hashlib import md5
from copy import copy

class User(drink.Page):

    drink_name = None

    mime = "user"

    description = u"User object"

    password = ''

    email = ''

    classes = {}

    groups = set()

    default_action = "view"

    default_read_groups = set()

    default_write_groups = set()

    editable_fields = {}

    owner_fields = {
    # FIXME: Don't look ordered by group !
        'title': copy(drink.Page.editable_fields['title']),
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

    def __init__(self, name, rootpath=None):

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

    def repair(self):
        drink.Page.repair(self)
        self.groups = set(self.groups)

    @property
    def html(self):
        d = self.__dict__.copy()
        client_id = drink.request.identity.id
        # request handling
        isaf = drink.request.params.get('is_friend', '')
        if isaf == '1':
            self.groups.add(client_id)
        elif isaf == '0':
            self.groups.remove(client_id)
        # produce view code
        users = drink.db.db[u'users']
        d['friends'] = u', '.join(users[o].id for o in self.groups if o != self.id)
        r = [ u'''
        <h2>%(id)s</h2>
        <div class="entry"><strong>Name</strong>: %(name)s
        </div><div class="entry"><strong>Surname</strong>: %(surname)s
        </div><div class="entry"><strong>Phones</strong>: %(phones)r
        </div>
        ''']
        if len(self.groups) > 1:
            r.append(u'<div class="entry"><strong>Friends</strong>: %(friends)s</div>')
        else:
            r.append(u'No friend yet...')
        if self.id != client_id:
            if client_id not in self.groups:
                r.append(u'<div class="entry"><button class="button"><a href="./?is_friend=1">I know and trust this user :)</a></button></div>')
            else:
                r.append(u'''<div class="entry"><button class="button"><a href="./?is_friend=0">I DON'T know and trust this user !</a></button></div>''')
        return u'\n'.join(r)%d

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
