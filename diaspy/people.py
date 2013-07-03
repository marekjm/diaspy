import re
from diaspy.streams import Outer
from diaspy.models import Aspect


class User():
    """This class abstracts a D* user.
    This object goes around the limitations of current D* API and will
    extract user data using black magic.
    However, no chickens are harmed when you use it.

    The parameter fetch should be either 'posts', 'data' or 'none'. By
    default it is 'posts' which means in addition to user data, stream
    will be fetched. If user has not posted yet diaspy will not be able 
    to extract the information from his/her posts. Since there is no official 
    way to do it we rely on user posts. If this will be the case user 
    will be notified with appropriate exception message.
    
    If fetch is 'data', only user data will be fetched. If the user is
    not found, no exception will be returned.

    When creating new User() one can pass either guid, handle and/or id as
    optional parameters. GUID takes precedence over handle when fetching
    user stream. When fetching user data, handle is required.
    """
    data = {}
    stream = []

    def __init__(self, connection, guid='', handle='', fetch='posts', id=0):
        self._connection = connection
        self.data = {
            'guid': guid,
            'handle': handle,
            'id': id
        }
        self._do_fetch(fetch)

    def __getitem__(self, key):
        return self.data[key]

    def _do_fetch(self, fetch):
        if fetch == 'posts':
            if self['handle'] and self['guid']: self.fetchguid()
            elif self['guid'] and not self['handle']: self.fetchguid()
            elif self['handle'] and not self['guid']: self.fetchhandle()
        elif fetch == 'data' and len(self['handle']):
            self.fetchprofile()

    def _sephandle(self):
        """Separate D* handle into pod pod and user.

        :returns: two-tuple (pod, user)
        """
        if re.match('^[a-zA-Z]+[a-zA-Z0-9_-]*@[a-z0-9.]+\.[a-z]+$', self['handle']) is None:
            raise Exception('invalid handle: {0}'.format(self['handle']))
        handle = self['handle'].split('@')
        pod, user = handle[1], handle[0]
        return (pod, user)
        
    def _finalize_data(self, data, names):
        final = {}
        for d, f in names:
            final[f] = data[d]
        return final

    def _postproc(self, request):
        """Makes necessary modifications to user data and
        sets up a stream.

        :param request: request object
        :type request: request
        """
        if request.status_code != 200:
            raise Exception('wrong error code: {0}'.format(request.status_code))
        else:
            request = request.json()
        if not len(request): raise Exception('Cannot extract user data: no posts to analyze')
        names = [('id', 'id'),
                 ('diaspora_id', 'diaspora_id'),
                 ('guid', 'guid'),
                 ('name', 'diaspora_name'),
                 ('avatar', 'image_urls'),
                 ]
        self.data = self._finalize_data(request[0]['author'], names)
        self.stream = Outer(self._connection, location='people/{0}.json'.format(self['guid']))

    def fetchhandle(self, protocol='https'):
        """Fetch user data and posts using Diaspora handle.
        """
        pod, user = self._sephandle()
        request = self._connection.session.get('{0}://{1}/u/{2}.json'.format(protocol, pod, user))
        self._postproc(request)

    def fetchguid(self):
        """Fetch user data and posts using guid.
        """
        request = self._connection.get('people/{0}.json'.format(self['guid']))
        self._postproc(request)
        
    def fetchprofile(self, protocol='https'):
        """Fetch user data using Diaspora handle.
        """
        request = self._connection.get('people.json?q={0}'.format(self['handle']))
        if request.status_code != 200:
            raise Exception('wrong error code: {0}'.format(request.status_code))
        else:
            request = request.json()
        if len(request):
            names = [('id', 'id'),
                     ('handle', 'diaspora_id'),
                     ('guid', 'guid'),
                     ('name', 'diaspora_name'),
                     ('avatar', 'image_urls'),
                     ]
            self.data = self._finalize_data(request[0], names)


class Contacts():
    """This class represents user's list of contacts.
    """
    def __init__(self, connection):
        self._connection = connection

    def add(self, user_id, aspect_ids):
        """Add user to aspects of given ids.

        :param user_id: user guid
        :type user_id: str
        :param aspect_ids: list of aspect ids
        :type aspect_ids: list
        """
        for aid in aspect_ids: Aspect(self._connection, aid).addUser(user_id)

    def remove(self, user_id, aspect_ids):
        """Remove user from aspects of given ids.

        :param user_id: user guid
        :type user_id: str
        :param aspect_ids: list of aspect ids
        :type aspect_ids: list
        """
        for aid in aspect_ids: Aspect(self._connection, aid).removeUser(user_id)

    def get(self, set=''):
        """Returns list of user contacts.
        Contact is a User() who is in one or more of user's
        aspects.

        By default, it will return list of users who are in
        user's aspects.

        If `set` is `all` it will also include users who only share
        with logged user and are not in his/hers aspects.

        If `set` is `only_sharing` it will return users who are only
        sharing with logged user and ARE NOT in his/hers aspects.

        :param set: if passed could be 'all' or 'only_sharing'
        :type set: str
        """
        params = {}
        if set: params['set'] = set

        request = self._connection.get('contacts.json', params=params)
        if request.status_code != 200:
            raise Exception('status code {0}: cannot get contacts'.format(request.status_code))
        contacts = [User(self._connection, user['guid'], user['handle'], 'none', user['id']) for user in request.json()]
        return contacts
