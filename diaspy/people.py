#!/usr/bin/env python3

import json
import re
import warnings

from diaspy.streams import Outer
from diaspy.models import Aspect
from diaspy import errors
from diaspy import search


def sephandle(handle):
    """Separate Diaspora* handle into pod pod and user.

    :returns: two-tuple (pod, user)
    """
    if re.match('^[a-zA-Z]+[a-zA-Z0-9_-]*@[a-z0-9.]+\.[a-z]+$', handle) is None:
        raise errors.InvalidHandleError('{0}'.format(handle))
    handle = handle.split('@')
    pod, user = handle[1], handle[0]
    return (pod, user)


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
    def __init__(self, connection, guid='', handle='', fetch='posts', id=0):
        self._connection = connection
        self.stream = []
        self.data = {
            'guid': guid,
            'handle': handle,
            'id': id,
        }
        self._fetch(fetch)

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return self['guid']

    def __repr__(self):
        return '{0} ({1})'.format(self['name'], self['guid'])

    def _fetchstream(self):
        self.stream = Outer(self._connection, location='people/{0}.json'.format(self['guid']))

    def _fetch(self, fetch):
        """Fetch user posts or data.
        """
        if fetch == 'posts':
            if self['handle'] and not self['guid']: self.fetchhandle()
            else: self.fetchguid()
        elif fetch == 'data' and self['handle']:
            self.fetchprofile()

    def _finalize_data(self, data):
        """Adjustments are needed to have similar results returned
        by search feature and fetchguid()/fetchhandle().
        """
        names = [('id', 'id'),
                 ('guid', 'guid'),
                 ('name', 'name'),
                 ('avatar', 'avatar'),
                 ('handle', 'diaspora_id'),
                 ]
        final = {}
        for f, d in names:
            final[f] = data[d]
        return final

    def _postproc(self, request):
        """Makes necessary modifications to user data and
        sets up a stream.

        :param request: request object
        :type request: request
        """
        if request.status_code != 200: raise Exception('wrong error code: {0}'.format(request.status_code))
        request = request.json()
        if not len(request): raise errors.UserError('cannot extract user data: no posts to analyze')
        self.data = self._finalize_data(request[0]['author'])

    def fetchhandle(self, protocol='https'):
        """Fetch user data and posts using Diaspora handle.
        """
        pod, user = sephandle(self['handle'])
        request = self._connection.get('{0}://{1}/u/{2}.json'.format(protocol, pod, user), direct=True)
        self._postproc(request)
        self._fetchstream()

    def fetchguid(self):
        """Fetch user data and posts using guid.
        """
        if self['guid']:
            request = self._connection.get('people/{0}.json'.format(self['guid']))
            self._postproc(request)
            self._fetchstream()
        else:
            raise errors.UserError('GUID not set')

    def fetchprofile(self):
        """Fetches user data.
        """
        data = search.Search(self._connection).user(self['handle'])
        if not data:
            warnings.warn('user with handle "{0}" has not been found on pod "{1}"'.format(self['handle'], self._connection.pod))
        else:
            self.data = data[0]

    def getHCard(self):
        """Returns XML string containing user HCard.
        """
        request = self._connection.get('hcard/users/{0}'.format(self['guid']))
        if request.status_code != 200: raise errors.UserError('could not fetch hcard for user: {0}'.format(self['guid']))
        return request.text


class Me():
    """Object represetnting current user.
    """
    _userinfo_regex = re.compile(r'window.current_user_attributes = ({.*})')
    _userinfo_regex_2 = re.compile(r'gon.user=({.*});gon.preloads')

    def __init__(self, connection):
        self._connection = connection

    def getInfo(self):
        """This function returns the current user's attributes.

        :returns: dict
        """
        request = self._connection.get('bookmarklet')
        userdata = self._userinfo_regex.search(request.text)
        if userdata is None: userdata = self._userinfo_regex_2.search(request.text)
        if userdata is None: raise errors.DiaspyError('cannot find user data')
        userdata = userdata.group(1)
        return json.loads(userdata)


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
        return [User(self._connection, guid=user['guid'], handle=user['handle'], fetch=None) for user in request.json()]
