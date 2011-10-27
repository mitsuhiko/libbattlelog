import json
import requests
import urlparse
import urllib


def url_quote(string):
    return urllib.quote_plus(unicode(string).encode('utf-8'))


class Battlelog(object):
    base_url = 'http://battlelog.battlefield.com/bf3/'

    def __init__(self, email, password):
        self.session = requests.session()

        rv = self.request('POST', 'gate/login/', data={
            'redirect':     '',
            'submit':       'Sign in',
            'email':        email,
            'password':     password
        })
        if 'Wrong email or password' in rv.content:
            raise RuntimeError('Could not login')

    def request(self, method, url, *args, **kwargs):
        url = urlparse.urljoin(self.base_url, url)
        return self.session.request(method, url, *args, **kwargs)

    def api_request(self, method, url, *args, **kwargs):
        headers = kwargs.setdefault('headers', {})
        headers['X-Requested-With'] = 'XMLHttpRequest'
        headers['X-AjaxNavigation'] = '1'
        return json.loads(self.request(method, url, *args, **kwargs).content)

    def get_user(self, username):
        rv = self.api_request('GET', 'user/%s/' % url_quote(username))
        user = rv['context'].get('profileCommon')
        if not user:
            return None
        return User(self, user)

    def get_platoon_members(self, id):
        rv = self.api_request('GET', 'platoon/%s/listmembers' % id)
        return [User(self, x) for x in rv['context']['listMembers']]


class User(object):

    def __init__(self, battlelog, profile_common):
        self.battlelog = battlelog
        self.profile_common = profile_common

    def _accessor(path):
        parts = tuple(path.split('.'))
        def getter(self):
            node = self.profile_common
            for part in parts:
                node = node.get(part)
            if node is None:
                return None
            return node
        return property(getter)

    @property
    def profile_url(self):
        return urlparse.urljoin(self.battlelog.base_url,
            'user/' + url_quote(self.username))

    def get_avatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?s=%s&d=%s' % (
            self.gravatar,
            size,
            'mm'
        )

    username = _accessor('user.username')
    gravatar = _accessor('user.gravatarMd5')
    user_id = _accessor('user.userId')
    status_message = _accessor('userStatusMessage.statusMessage')
    veteran_status = _accessor('veteranStatus.status')
    friend_count = _accessor('friendCount')
    location = _accessor('userinfo.location')
    age = _accessor('userinfo.age')
    name = _accessor('userinfo.name')
    is_online = _accessor('user.presence.isOnline')
    is_playing = _accessor('user.presence.isPlaying')
    server_guid = _accessor('user.presence.serverGuid')
    server_name = _accessor('user.presence.serverName')

    @property
    def is_playing(self):
        rv = False
        try:
            self.profile_common['user']['presence']['serverGuid']
            rv = self.profile_common['user']['presence']['isPlaying']
        except KeyError:
            pass
        return rv

    @property
    def server_url(self):
        return urlparse.urljoin(self.battlelog.base_url,
            'servers/show/%s/%s/' % (url_quote(self.server_guid),
                                     url_quote(self.server_name)))

    def __repr__(self):
        return '<User "%s" (%s)>' % (self.username, self.user_id)
