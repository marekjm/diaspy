#!/usr/bin/env python3


import json
import re

from diaspy import errors


"""This module is only imported in other diaspy modules and
MUST NOT import anything.
"""


class Aspect():
    """This class represents an aspect.

    Class can be initialized by passing either an id and/or name as
    parameters.
    If both are missing, an exception will be raised.
    """
    def __init__(self, connection, id=None, name=None):
        self._connection = connection
        self.id, self.name = id, name
        if id and not name:
            self.name = self._findname()
        elif name and not id:
            self.id = self._findid()
        elif not id and not name:
            raise Exception("Aspect must be initialized with either an id or name")

    def _findname(self):
        """Finds name for aspect.
        """
        name = None
        aspects = self._connection.getUserInfo()['aspects']
        for a in aspects:
            if a['id'] == self.id:
                name = a['name']
                break
        return name

    def _findid(self):
        """Finds id for aspect.
        """
        id = None
        aspects = self._connection.getUserInfo()['aspects']
        for a in aspects:
            if a['name'] == self.name:
                id = a['id']
                break
        return id

    def _getajax(self):
        """Returns HTML returned when editing aspects via web UI.
        """
        start_regexp = re.compile('<ul +class=["\']contacts["\'] *>')
        ajax = self._connection.get('aspects/{0}/edit'.format(self.id)).text

        begin = ajax.find(start_regexp.search(ajax).group(0))
        end = ajax.find('</ul>')
        return ajax[begin:end]

    def _extractusernames(self, ajax):
        """Extracts usernames and GUIDs from ajax returned by Diaspora*.
        Returns list of two-tuples: (guid, diaspora_name).
        """
        userline_regexp = re.compile('<a href=["\']/people/[a-z0-9]{16,16}["\']>[\w()*@. -]+</a>')
        return [(line[17:33], re.escape(line[35:-4])) for line in userline_regexp.findall(ajax)]

    def _extractpersonids(self, ajax, usernames):
        """Extracts `person_id`s and usernames from ajax and list of usernames.
        Returns list of two-tuples: (username, id)
        """
        personid_regexp = 'alt=["\']{0}["\'] class=["\']avatar["\'] data-person_id=["\'][0-9]+["\']'
        personids = [re.compile(personid_regexp.format(name)).search(ajax).group(0) for guid, name in usernames]
        for n, line in enumerate(personids):
            i, id = -2, ''
            while line[i].isdigit():
                id = line[i] + id
                i -= 1
            personids[n] = (usernames[n][1], id)
        return personids

    def _defineusers(self, ajax, personids):
        """Gets users contained in this aspect by getting users who have `delete` method.
        """
        method_regexp = 'data-method="delete" data-person_id="{0}"'
        users = []
        for name, id in personids:
            if re.compile(method_regexp.format(id)).search(ajax): users.append(name)
        return users

    def _getguids(self, users_in_aspect, usernames):
        """Defines users contained in this aspect.
        """
        guids = []
        for guid, name in usernames:
            if name in users_in_aspect: guids.append(guid)
        return guids

    def getUsers(self):
        """Returns list of GUIDs of users who are listed in this aspect.
        """
        ajax = self._getajax()
        usernames = self._extractusernames(ajax)
        personids = self._extractpersonids(ajax, usernames)
        users_in_aspect = self._defineusers(ajax, personids)
        return self._getguids(users_in_aspect, usernames)

    def addUser(self, user_id):
        """Add user to current aspect.

        :param user_id: user to add to aspect
        :type user_id: int
        :returns: JSON from request
        """
        data = {'authenticity_token': repr(self._connection),
                'aspect_id': self.id,
                'person_id': user_id}

        request = self._connection.post('aspect_memberships.json', data=data)

        if request.status_code == 400:
            raise errors.AspectError('duplicate record, user already exists in aspect: {0}'.format(request.status_code))
        elif request.status_code == 404:
            raise errors.AspectError('user not found from this pod: {0}'.format(request.status_code))
        elif request.status_code != 200:
            raise errors.AspectError('wrong status code: {0}'.format(request.status_code))
        return request.json()

    def removeUser(self, user_id):
        """Remove user from current aspect.

        :param user_id: user to remove from aspect
        :type user: int
        """
        data = {'authenticity_token': self._connection.get_token(),
                'aspect_id': self.id,
                'person_id': user_id}
        request = self.connection.delete('aspect_memberships/{0}.json'.format(self.id), data=data)

        if request.status_code != 200:
            raise errors.AspectError('cannot remove user from aspect: {0}'.format(request.status_code))
        return request.json()


class Notification():
    """This class represents single notification.
    """
    _who_regexp = re.compile(r'/people/[0-9a-z]+" class=\'hovercardable')
    _when_regexp = re.compile(r'[0-9]{4,4}(-[0-9]{2,2}){2,2} [0-9]{2,2}(:[0-9]{2,2}){2,2} UTC')

    def __init__(self, connection, data):
        self._connection = connection
        self.type = list(data.keys())[0]
        self.data = data[self.type]
        self.id = self.data['id']
        self.unread = self.data['unread']

    def __getitem__(self, key):
        """Returns a key from notification data.
        """
        return self.data[key]

    def __str__(self):
        """Returns notification note.
        """
        string = re.sub('</?[a-z]+( *[a-z_-]+=["\'][\w():.,!?#/\- ]*["\'])* */?>', '', self.data['note_html'])
        string = string.strip().split('\n')[0]
        while '  ' in string: string = string.replace('  ', ' ')
        return string

    def __repr__(self):
        """Returns notification note with more details.
        """
        return '{0}: {1}'.format(self.when(), str(self))

    def who(self):
        """Returns list of guids of the users who caused you to get the notification.
        """
        return [who[8:24] for who in self._who_regexp.findall(self.data['note_html'])]

    def when(self):
        """Returns UTC time as found in note_html.
        """
        return self._when_regexp.search(self.data['note_html']).group(0)

    def mark(self, unread=False):
        """Marks notification to read/unread.
        Marks notification to read if `unread` is False.
        Marks notification to unread if `unread` is True.

        :param unread: which state set for notification
        :type unread: bool
        """
        headers = {'x-csrf-token': repr(self._connection)}
        params = {'set_unread': json.dumps(unread)}
        self._connection.put('notifications/{0}'.format(self['id']), params=params, headers=headers)
        self.data['unread'] = unread


class Post():
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.
    """
    def __init__(self, connection, id, fetch=True):
        """
        :param id: id or guid of the post
        :type id: str
        :param connection: connection object used to authenticate
        :type connection: connection.Connection
        """
        self._connection = connection
        self.id = id
        if fetch: self._fetch()

    def __repr__(self):
        """Returns string containing more information then str().
        """
        data = self.get_data()
        return '{0} ({1}): {2}'.format(data['author']['name'], data['author']['diaspora_id'], data['text'])

    def __str__(self):
        """Returns text of a post.
        """
        return self.get_data()['text']

    def _fetch(self):
        """This function retrieves data of the post.
        """
        request = self._connection.get('posts/{0}.json'.format(self.post_id))
        if request.status_code != 200:
            raise errors.PostError('wrong status code: {0}'.format(request.status_code))
        else:
            self.data = request.json()

    def like(self):
        """This function likes a post.
        It abstracts the 'Like' functionality.

        :returns: dict -- json formatted like object.
        """
        data = {'authenticity_token': repr(self._connection)}

        request = self._connection.post('posts/{0}/likes'.format(self.post_id),
                                  data=data,
                                  headers={'accept': 'application/json'})

        if request.status_code != 201:
            raise errors.PostError('{0}: Post could not be liked.'
                            .format(request.status_code))
        return request.json()

    def delete_like(self):
        """This function removes a like from a post
        """
        data = {'authenticity_token': self._connection.get_token()}

        request = self._connection.delete('posts/{0}/likes/{1}'
                                    .format(self.post_id,
                                            self.data['interactions']
                                                     ['likes'][0]['id']),
                                    data=data)
        if request.status_code != 204:
            raise errors.PostError('{0}: Like could not be removed.'
                            .format(request.status_code))

    def reshare(self):
        """This function reshares a post
        """
        data = {'root_guid': self.data['guid'],
                'authenticity_token': repr(self._connection)}

        request = self._connection.post('reshares',
                                  data=data,
                                  headers={'accept': 'application/json'})
        if request.status_code != 201:
            raise Exception('{0}: Post could not be reshared'.format(request.status_code))
        return request.json()

    def comment(self, text):
        """This function comments on a post

        :param text: text to comment.
        :type text: str
        """
        data = {'text': text,
                'authenticity_token': repr(self._connection)}
        request = self._connection.post('posts/{0}/comments'.format(self.id),
                                  data=data,
                                  headers={'accept': 'application/json'})

        if request.status_code != 201:
            raise Exception('{0}: Comment could not be posted.'
                            .format(request.status_code))
        return request.json()

    def delete_comment(self, comment_id):
        """This function removes a comment from a post

        :param comment_id: id of the comment to remove.
        :type comment_id: str
        """
        data = {'authenticity_token': repr(self._connection)}
        request = self._connection.delete('posts/{0}/comments/{1}'
                                    .format(self.id,
                                            comment_id),
                                    data=data,
                                    headers={'accept': 'application/json'})

        if request.status_code != 204:
            raise errors.PostError('{0}: Comment could not be deleted'
                            .format(request.status_code))

    def delete(self):
        """ This function deletes this post
        """
        data = {'authenticity_token': repr(self._connection)}
        request = self._connection.delete('posts/{0}'.format(self.id),
                                    data=data,
                                    headers={'accept': 'application/json'})
        if request.status_code != 204:
            raise errors.PostError('{0}: Post could not be deleted'.format(request.status_code))
