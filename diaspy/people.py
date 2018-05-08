#!/usr/bin/env python3

import json
import re
import warnings
import time

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
    @classmethod
    def parse(cls, connection, data):
        person = data.get('person')
        if person is None:
            raise errors.KeyMissingFromFetchedData('person', data)

        guid = person.get('guid')
        if guid is None:
            raise errors.KeyMissingFromFetchedData('guid', person)

        handle = person.get('diaspora_id')
        if handle is None:
            raise errors.KeyMissingFromFetchedData('diaspora_id', person)

        person_id = person.get('id')
        if person_id is None:
            raise errors.KeyMissingFromFetchedData('id', person)

        return User(connection, guid, handle, id, data=data)

    def __init__(self, connection, guid='', handle='', fetch='posts', id=0, data=None):
        self._connection = connection
        self.stream = []
        self.data = {
            'guid': guid,
            'handle': handle,
            'id': id,
        }
        self.photos = []
        if data: self.data.update( data )
        if fetch: self._fetch(fetch)

    def __getitem__(self, key):
        return self.data[key]

    def __str__(self):
        return self.data.get('guid', '<guid missing>')

    def __repr__(self):
        return '{0} ({1})'.format(self.handle(), self.guid())

    def handle(self):
        if 'handle' in self.data: return self['handle']
        return self.data.get('diaspora_id', 'Unknown handle')

    def guid(self):
        return self.data.get('guid', '<guid missing>')

    def id(self):
        return self.data['id']

    def _fetchstream(self):
        self.stream = Outer(self._connection, guid=self['guid'])

    def _fetch(self, fetch):
        """Fetch user posts or data.
        """
        if fetch == 'posts':
            if self.handle() and not self['guid']: self.fetchhandle()
            else: self.fetchguid()
        elif fetch == 'data' and self['handle']:
            self.fetchprofile()

    def _finalize_data(self, data):
        """Adjustments are needed to have similar results returned
        by search feature and fetchguid()/fetchhandle().
        """
        return data

    def _postproc(self, request):
        """Makes necessary modifications to user data and
        sets up a stream.

        :param request: request object
        :type request: request
        """
        if request.status_code != 200: raise Exception('wrong error code: {0}'.format(request.status_code))
        data = request.json()
        self.data = self._finalize_data(data)

    def fetchhandle(self, protocol='https'):
        """Fetch user data and posts using Diaspora handle.
        """
        pod, user = sephandle(self['handle'])
        request = self._connection.get('{0}://{1}/u/{2}.json'.format(protocol, pod, user), direct=True)
        self._postproc(request)
        self._fetchstream()

    def fetchguid(self, fetch_stream=True):
        """Fetch user data and posts (if fetch_stream is True) using guid.
        """
        if self['guid']:
            request = self._connection.get('people/{0}.json'.format(self['guid']))
            self._postproc(request)
            if fetch_stream: self._fetchstream()
        else:
            raise errors.UserError('GUID not set')

    def fetchprofile(self):
        """Fetches user data.
        """ 
        data = search.Search(self._connection).user(self.handle())
        if not data:
            raise errors.UserError('user with handle "{0}" has not been found on pod "{1}"'.format(self.handle(), self._connection.pod))
        else:
            self.data.update( data[0] )

    def aspectMemberships(self):
        if 'contact' in self.data:
            return self.data.get('contact', {}).get('aspect_memberships', [])
        else:
            return self.data.get('aspect_memberships', [])

    def getPhotos(self):
        """
        --> GET /people/{GUID}/photos.json HTTP/1.1

        <-- HTTP/1.1 200 OK

        {
            "photos":[
                {
                    "id":{photo_id},
                    "guid":"{photo_guid}",
                    "created_at":"2018-03-08T23:48:31.000Z",
                    "author":{
                        "id":{author_id},
                        "guid":"{author_guid}",
                        "name":"{author_name}",
                        "diaspora_id":"{diaspora_id}",
                        "avatar":{"small":"{avatar_url_small}","medium":"{avatar_url_medium}","large":"{avatar_url_large}"}
                    },
                    "sizes":{
                        "small":"{photo_url}",
                        "medium":"{photo_url}",
                        "large":"{photo_url}"
                    },
                    "dimensions":{"height":847,"width":998},
                    "status_message":{
                        "id":{post_id}
                    }
                },{ ..
        }

        if there are no photo's it returns:
        {"photos":[]}
        """

        request = self._connection.get('/people/{0}/photos.json'.format(self['guid']))
        if request.status_code != 200: raise errors.UserError('could not fetch photos for user: {0}'.format(self['guid']))

        json = request.json()
        if json: self.photos = json['photos']
        return json['photos']

    def getHCard(self):
        """Returns json containing user HCard.
        --> /people/{guid}/hovercard.json?_={timestamp}

        <-- HTTP/2.0 200 OK
        {
            "id":123,
            "guid":"1234567890abcdef",
            "name":"test",
            "diaspora_id":"batman@test.test",
            "contact":false,
            "profile":{
                "avatar":"https://nicetesturl.url/image.jpg",
                "tags":["tag1", "tag2", "tag3", "tag4", "tag5"]}
        }
        """
        timestamp = int(time.mktime(time.gmtime()))
        request = self._connection.get('/people/{0}/hovercard.json?_={}'.format(self['guid'], timestamp))
        if request.status_code != 200: raise errors.UserError('could not fetch hcard for user: {0}'.format(self['guid']))
        return request.json()

    def deletePhoto(self, photo_id):
        """
        --> DELETE /photos/{PHOTO_ID} HTTP/1.1
        <-- HTTP/1.1 204 No Content
        """
        request = self._connection.delete('/photos/{0}'.format(photo_id))
        if request.status_code != 204: raise errors.UserError('could not delete photo_id: {0}'.format(photo_id))

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
    def __init__(self, connection, fetch=False, set=''):
        self._connection = connection
        self.contacts = None
        if fetch: self.contacts = self.get(set)

    def __getitem__(self, index):
        return self.contacts[index]

    def addAspect(self, name, visible=False):
        """
        --> POST /aspects HTTP/1.1
        --> {"person_id":null,"name":"test","contacts_visible":false}

        <-- HTTP/1.1 200 OK

        Add new aspect.

        TODO: status_code's

        :param name: aspect name to add
        :type name: str
        :param visible: sets if contacts in aspect are visible for each and other
        :type visible: bool
        :returns: JSON from request
        """
        data = {
            'person_id': None,
            'name': name,
            'contacts_visible': visible
        }
        headers={'content-type': 'application/json',
                 'accept': 'application/json' }
        request = self._connection.tokenFrom('contacts').post('aspects', headers=headers, data=json.dumps(data))

        if request.status_code == 400:
            raise errors.AspectError('duplicate record, aspect alreadt exists: {0}'.format(request.status_code))
        elif request.status_code != 200:
            raise errors.AspectError('wrong status code: {0}'.format(request.status_code))

        new_aspect = request.json()
        self._connection.userdata()['aspects'].append( new_aspect )

        return new_aspect

    def deleteAspect(self, aspect_id):
        """
        --> POST /aspects/{ASPECT_ID} HTTP/1.1
            _method=delete&authenticity_token={TOKEN}
            Content-Type: application/x-www-form-urlencoded

        <-- HTTP/1.1 302 Found
            Content-Type: text/html; charset=utf-8
        """
        request = self._connection.tokenFrom('contacts').delete('aspects/{}'.format( aspect_id ))

        if request.status_code != 200: # since we don't post but delete
            raise errors.AspectError('wrong status code: {0}'.format(request.status_code))

    def add(self, user_id, aspect_ids):
        """Add user to aspects of given ids.

        :param user_id: user id (not guid)
        :type user_id: str
        :param aspect_ids: list of aspect ids
        :type aspect_ids: list
        """
        # TODO update self.contacts
        # Returns {"aspect_id":123,"person_id":123}
        for aid in aspect_ids:
            new_aspect_membership = Aspect(self._connection, aid).addUser(user_id)

            # user.
            if new_aspect_membership:
                for user in self.contacts:
                    if int(user.data['person_id']) == int(user_id):
                        user.data['aspect_memberships'].append( new_aspect_membership )
                        return new_aspect_membership

    def remove(self, user_id, aspect_ids):
        """Remove user from aspects of given ids.

        :param user_id: user id
        :type user_id: str
        :param aspect_ids: list of aspect ids
        :type aspect_ids: list
        """
        for aid in aspect_ids: Aspect(self._connection, aid).removeUser(user_id)

    def get(self, set='', page=0):
        """Returns list of user contacts.
        Contact is a User() who is in one or more of user's
        aspects.

        By default, it will return list of users who are in
        user's aspects.

        If `set` is `all` it will also include users who only share
        with logged user and are not in his/hers aspects.

        If `set` is `only_sharing` it will return users who are only
        sharing with logged user and ARE NOT in his/hers aspects.

        # On "All contacts" button diaspora
        on the time of testing this I had 20 contacts and 10 that 
        where only sharing with me. So 30 in total.

        -->    GET /contacts?set=all HTTP/1.1
            <-- HTTP/1.1 200 OK
            returned 25 contacts (5 only sharing with me)

        -->    GET /contacts.json?page=1&set=all&_=1524410225376 HTTP/1.1
            <-- HTTP/1.1 200 OK
            returned the same list as before.

        --> GET /contacts.json?page=2&set=all&_=1524410225377 HTTP/1.1
            <-- HTTP/1.1 200 OK
            returned the other 5 that where only sharing with me.

        --> GET /contacts.json?page=3&set=all&_=1524410225378 HTTP/1.1
            <-- HTTP/1.1 200 OK
            returned empty list.

        It appears that /contacts?set=all returns a maximum of 25 
        contacts.

        So if /contacts?set=all returns 25 contacts then request next 
        page until page returns a list with less then 25. I don't see a 
        reason why we should request page=1 'cause the previous request 
        will be the same. So begin with page=2 if /contacts?set=all 
        returns 25.

        :param set: if passed could be 'all' or 'only_sharing'
        :type set: str
        """
        params = {}
        if set:
            params['set'] = set
            params['_'] = int(time.mktime(time.gmtime()))
            if page: params['page'] = page

        request = self._connection.get('contacts.json', params=params)
        if request.status_code != 200:
            raise Exception('status code {0}: cannot get contacts'.format(request.status_code))

        json = request.json()
        users = [User.parse(self._connection, each) for each in json]
        if len(json) == 25:
            if not page: page = 1
            users += self.get(set=set, page=page+1)
        return users
