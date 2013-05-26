import re
from diaspy.streams import Outer


class User:
    """This class abstracts a D* user.
    This object goes around the limitations of current D* API and will
    extract user data using black magic.
    However, no chickens are harmed when you use it.

    If user has not posted yet diaspy will not be able to extract the information 
    from his/her posts. Since there is no official way to do it we rely
    on user posts. If this will be the case user will be notified with appropriate
    exception message.

    When creating new User() one can pass either guid or handle as 
    an optional parameter. GUID takes precedence over handle.
    """
    data = {}
    stream = []

    def __init__(self, connection, guid='', handle=''):
        self._connection = connection
        self.guid, self.handle = guid, handle
        if handle and guid: self.fetchguid(guid)
        elif guid and not handle: self.fetchguid(guid)
        elif handle and not guid: self.fetchhandle(handle)

    def __getitem__(self, key):
        return self.data[key]

    def _sephandle(self, handle):
        """Separate D* handle into pod pod and user.

        :param handle: diaspora id: user@pod.example.com
        :type handle: str
        :returns: two-tuple (pod, user)
        """
        if re.match('^[a-zA-Z]+[a-zA-Z0-9_-]*@[a-z0-9.]+\.[a-z]+$', handle) is None:
            raise Exception('invalid handle: {0}'.format(handle))
        handle = handle.split('@')
        pod, user = handle[1], handle[0]
        return (pod, user)

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

        if not len(request): raise ('Cannot extract user data: no posts to analyze')
        data = request[0]['author']
        final = {}
        names = [('id', 'id'),
                 ('diaspora_id', 'diaspora_id'),
                 ('guid', 'guid'),
                 ('name', 'diaspora_name'),
                 ('avatar', 'image_urls'),
                 ]
        for d, f in names:
            final[f] = data[d]
        self.data = final
        self.stream = Outer(self._connection, location='people/{0}.json'.format(self.data['guid']))

    def fetchhandle(self, diaspora_id, protocol='https'):
        """Fetch user data using Diaspora handle.
        """
        pod, user = self._sephandle(diaspora_id)
        request = self._connection.session.get('{0}://{1}/u/{2}.json'.format(protocol, pod, user))
        self._postproc(request)

    def fetchguid(self, guid):
        """Fetch user data using guid.
        """
        request = self._connection.get('people/{0}.json'.format(guid))
        self._postproc(request)


class Contacts():
    """This class represents user's list of contacts.
    """
    def __init__(self, connection):
        self._connection = connection

    def get_only_sharing(self):
        """Returns contacts who are only sharing with you.

        :returns: list
        """
        params = {'set':'only_sharing'}
        request = self._connection.get('contacts.json', params=params)
        if request.status_code != 200:
            raise Exception('status code {0}: cannot get contacts'.format(request.status_code))
        contacts = [User(user['guid']) for user in request.json()]
        return contacts
