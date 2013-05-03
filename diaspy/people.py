import re
from diaspy.streams import Outer


class User:
    """This class abstracts a D* user.
    This object goes around the limitations of current D* API and will
    extract user data using black magic.
    However, no chickens are harmed when you use it.
    """
    def __init__(self, connection):
        self._connection = connection
        self.data = {}

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

    def _gethandle(self, diaspora_id, protocol='https'):
        """Get user data using handle.
        """
        pod, user = self._sephandle(diaspora_id)
        request = self._connection.session.get('{0}://{1}/u/{2}.json'.format(protocol, pod, user)).json()
        data = request[0]['author']
        self.data = data
        self.stream = Outer(self._connection, location='people/{0}.json'.format(self.data['guid']))

    def _getguid(self, guid):
        """Get user data using guid.
        """
        request = self._connection.get('people/{0}.json'.format(guid)).json()
        data = request[0]['author']
        self.data = data
        self.stream = Outer(self._connection, location='people/{0}.json'.format(self.data['guid']))

    def fetchguid(self, guid):
        """Fetch user data using guid.
        """
        self._getguid(guid)

    def fetchhandle(self, diaspora_id, protocol='https'):
        """Fetch user data using diaspora id.
        """
        self._gethandle(diaspora_id, protocol)
