#!/usr/bin/env python3


class Post:
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.
        Remember that you also need to be logged in.
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

    def __str__(self):
        """Returns text of a post.
        """
        return self.get_data['text']

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

        if request.status_code != 201:
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

        request = self.connection.delete('aspect_memberships/42.json', data=data)

        if request.status_code != 200:
            raise Exception('wrong status code: {0}'.format(request.status_code))
        return request.json()
