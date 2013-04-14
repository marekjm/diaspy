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

    def get_data(self):
        """This function retrieves data of the post.
        """
        r = self._connection.get('posts/{1}.json'.format(self.post_id))
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception('wrong status code: {0}'.format(r.status_code))

    def like(self):
        """This function likes a post.
        It abstracts the 'Like' functionality.

        :returns: dict -- json formatted like object.
        """
        data = {'authenticity_token': self._connection.getToken()}

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
        data = {'authenticity_token': self._connection.getToken()}

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
                'authenticity_token': self._connection.getToken()}

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
                'authenticity_token': self._connection.getToken()}

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
        data = {'authenticity_token': self._connection.getToken()}

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
        data = {'authenticity_token': self._connection.getToken()}
        r = self._connection.delete('posts/{0}'.format(self.post_id),
                                    data=data,
                                    headers={'accept': 'application/json'})
        if r.status_code != 204:
            raise Exception('{0}: Post could not be deleted'.format(r.status_code))
