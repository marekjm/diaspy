#!/usr/bin/env python3


import json
import re


"""This module is only imported in other diaspy modules and
MUST NOT import anything.
"""


class Aspect():
    """This class represents an aspect.
    """
    def __init__(self, connection, id=-1):
        self._connection = connection
        self.id = id
        self.name = ''

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
        string = re.sub('</?[a-z]+( *[a-z_-]+=["\'][a-zA-Z0-9/:_#.\- ]*["\'])* */?>', '', self.data['note_html'])
        string = string.strip().split('\n')[0]
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
