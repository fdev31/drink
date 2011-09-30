import drink
from . import libsonic
# http://www.subsonic.org/pages/api.jsp

class SonicHome(drink.Page):

    drink_name = "Subsonic"
    mime = "page"
    description = "A subsonic application"
    login = ""
    password = ""
    server = ""
    port = 443

    owner_fields = drink.Page.owner_fields.copy()
    owner_fields.update({
        'server': drink.types.Text('Server address', group='srv'),
        'port': drink.types.Int('Server port', group='srv'),
        'login': drink.types.Text(group='auth'),
        'password': drink.types.Password(group='auth'),
    })

    @property
    def html(self):
        s = self._v_logon
        yield '<h1>Chat</h1>'
        yield repr(s.getChatMessages())
        yield '<h1>Now playing</h1>'
        yield repr(s.getNowPlaying())
        yield '<h1>Playlists</h1>'
        for pls in s.getPlaylists()['playlists']['playlist']:
            yield '<h2>%r</h2>'%pls['name']
            #yield repr(s.getPlaylist(pls['id']))
        yield '<h1>Search</h1>'
        for song in s.search2(query='tango', songCount=5)['searchResult2']:
            yield repr(song)
        #print dir(s)
        #return repr(s.getRandomSongs(size=10))


    def view(self):
        s = getattr(self, '_v_logon', None)
        if s is None:
            s = libsonic.Connection(self.server, self.login, self.password, port=self.port)
            self._v_logon = s
        return drink.Page.view(self)
