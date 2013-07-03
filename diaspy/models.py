#!/usr/bin/env python3


import json
import re


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

    def getUsers(self):
        """Returns list of GUIDs of users who are listed in this aspect.
        """
        start_regexp = re.compile('<ul +class=["\']contacts["\'] *>')
        userline_regexp = re.compile('<a href=["\']/people/[a-z0-9]{16,16}["\']>[a-zA-Z0-9 _-]+</a>')
        personid_regexp = 'alt="{0}" class="avatar" data-person_id="[0-9]+"'
        method_regexp = 'data-method="delete" data-person_id="{0}"'

        ajax = self._connection.get('aspects/{0}/edit'.format(self.id)).text
        begin = ajax.find(start_regexp.search(ajax).group(0))
        end = ajax.find('</ul>')
        ajax = ajax[begin:end]

        usernames = [(line[17:33], line[35:-4]) for line in userline_regexp.findall(ajax)]
        personids = [re.compile(personid_regexp.format(name)).search(ajax).group(0) for guid, name in usernames]
        for n, line in enumerate(personids):
            i, id = -2, ''
            while line[i].isdigit():
                id = line[i] + id
                i -= 1
            personids[n] = (usernames[n][1], id)

        users_in_aspect = []
        for name, id in personids:
            if re.compile(method_regexp.format(id, self.id)).search(ajax): users_in_aspect.append(name)

        users = []
        for i, user in enumerate(usernames):
            guid, name = user
            if name in users_in_aspect:
                users.append(guid)
        return users

    def addUser(self, user_id):
        """Add user to current aspect.

        :param user_id: user to add to aspect
        :type user: int
        """
        data = {'authenticity_token': self._connection.get_token(),
                'aspect_id': self.id,
                'person_id': user_id}

        request = self._connection.post('aspect_memberships.json', data=data)

        if request.status_code == 400:
            raise Exception('duplicate record, user already exists in aspect: {0}'.format(request.status_code))
        elif request.status_code == 404:
            raise Exception('user not found from this pod: {0}'.format(request.status_code))
        elif request.status_code != 200:
            raise Exception('wrong status code: {0}'.format(request.status_code))
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
            raise Exception('wrong status code: {0}'.format(request.status_code))
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
        headers = {'x-csrf-token': self._connection.get_token()}
        params = {'set_unread': json.dumps(unread)}
        self._connection.put('notifications/{0}'.format(self['id']), params=params, headers=headers)
        self.data['unread'] = unread


class Post():
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.
    """
    def __init__(self, post_id, connection):
        """
        :param post_id: id or guid of the post
        :type post_id: str
        :param connection: connection object used to authenticate
        :type connection: connection.Connection
        """
        self._connection = connection
        self.post_id = post_id

    def __repr__(self):
        """Returns string containing more information then str().
        """
        data = self.get_data()
        return '{0} ({1}): {2}'.format(data['author']['name'], data['author']['diaspora_id'], data['text'])

    def __str__(self):
        """Returns text of a post.
        """
        return self.get_data()['text']

    def get_data(self):
        """This function retrieves data of the post.
        """
        r = self._connection.get('posts/{0}.json'.format(self.post_id))
        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))
        return r.json()

    def like(self):
        """This function likes a post.
        It abstracts the 'Like' functionality.

        :returns: dict -- json formatted like object.
        """
        data = {'authenticity_token': self._connection.get_token()}

        r = self._connection.post('posts/{0}/likes'.format(self.post_id),
                                  data=data,
                                  headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Post could not be liked.'
                            .format(r.status_code))

        return r.json()

    def delete_like(self):
        """This function removes a like from a post
        """
        data = {'authenticity_token': self._connection.get_token()}

        post_data = self.get_data()

        r = self._connection.delete('posts/{0}/likes/{1}'
                                    .format(self.post_id,
                                            post_data['interactions']
                                                     ['likes'][0]['id']),
                                    data=data)

        if r.status_code != 204:
            raise Exception('{0}: Like could not be removed.'
                            .format(r.status_code))

    def reshare(self):
        """This function reshares a post

        """
        post_data = self.get_data()

        data = {'root_guid': post_data['guid'],
                'authenticity_token': self._connection.get_token()}

        r = self._connection.post('reshares',
                                  data=data,
                                  headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Post could not be reshared.'
                            .format(r.status_code))

        return r.json()

    def comment(self, text):
        """This function comments on a post

        :param text: text to comment.
        :type text: str
        """
        data = {'text': text,
                'authenticity_token': self._connection.get_token()}

        r = self._connection.post('posts/{0}/comments'.format(self.post_id),
                                  data=data,
                                  headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Comment could not be posted.'
                            .format(r.status_code))

        return r.json()

    def delete_comment(self, comment_id):
        """This function removes a comment from a post

        :param comment_id: id of the comment to remove.
        :type comment_id: str
        """
        data = {'authenticity_token': self._connection.get_token()}

        r = self._connection.delete('posts/{0}/comments/{1}'
                                    .format(self.post_id,
                                            comment_id),
                                    data=data,
                                    headers={'accept': 'application/json'})

        if r.status_code != 204:
            raise Exception('{0}: Comment could not be deleted.'
                            .format(r.status_code))

    def delete(self):
        """ This function deletes this post
        """
        data = {'authenticity_token': self._connection.get_token()}
        r = self._connection.delete('posts/{0}'.format(self.post_id),
                                    data=data,
                                    headers={'accept': 'application/json'})
        if r.status_code != 204:
            raise Exception('{0}: Post could not be deleted'.format(r.status_code))
