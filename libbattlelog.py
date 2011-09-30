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


class User(object):

    def __init__(self, battlelog, profile_common):
        self.battlelog = battlelog
        self.profile_common = profile_common

    def _accessor(path):
        parts = tuple(path.split('.'))
        def getter(self):
            node = self.profile_common
            for part in parts:
                node = node[part]
            return node
        return property(getter)

    username = _accessor('user.username')
    gravatar = _accessor('user.gravatarMd5')
    user_id = _accessor('user.userId')
    status_message = _accessor('userStatusMessage.statusMessage')
    veteran_status = _accessor('veteranStatus.status')
    friend_count = _accessor('friendCount')
    location = _accessor('userinfo.location')
    age = _accessor('userinfo.age')
    name = _accessor('userinfo.name')

    def __repr__(self):
        return '<User "%s" (%s)>' % (self.username, self.user_id)
