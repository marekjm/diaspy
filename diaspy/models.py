import requests


class Post:
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.

    """

    def __init__(self, post_id, client):
        """
        :param post_id: id or guid of the post
        :type post_id: str
        :param client: client object used to authenticate
        :type client: client.Client

        .. note::
            The login function of the client should be called,
            before calling any of the post functions.

        """
        self._client = client
        self.post_id = post_id

    def get_data(self):
        r = self._client.session.get(self._client.pod +
                                     '/posts/' +
                                     self.post_id +
                                     '.json')
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception('wrong status code: ' + str(r.status_code))

    def like(self):
        """This function likes a post

        :returns: dict -- json formatted like object.

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      '/posts/' +
                                      self.post_id +
                                      '/likes',
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception(str(r.status_code) + ': Post could not be liked.')

        return r.json()

    def delete_like(self):
        """This function removes a like from a post

        """

        data = {'authenticity_token': self._client.get_token()}

        post_data = self.get_data()

        r = self._client.session.delete(self._client.pod + '/posts/' +
                                        self.post_id +
                                        '/likes/' +
                                        str(post_data['interactions']
                                            ['likes'][0]['id']),
                                        data=data)

        if r.status_code != 204:
            raise Exception(str(r.status_code) +
                            ': Like could not be removed.')

    def reshare(self):
        """This function reshares a post

        """

        post_data = self.get_data()

        data = {'root_guid': post_data['guid'],
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      '/reshares',
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception(str(r.status_code) +
                            ': Post could not be reshared.')

        return r.json()

    def comment(self, text):
        """This function comments on a post

        :param text: text to comment.
        :type text: str

        """

        data = {'text': text,
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      '/posts/' +
                                      self.post_id +
                                      '/comments',
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception(str(r.status_code) +
                            ': Comment could not be posted.')

        return r.json()

    def delete_comment(self, comment_id):
        """This function removes a comment from a post

        :param comment_id: id of the comment to remove.
        :type comment_id: str

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete(self._client.pod + '/posts/' +
                                        self.post_id +
                                        '/comments/' +
                                        comment_id,
                                        data=data,
                                        headers={'accept': 'application/json'})

        if r.status_code != 204:
            raise Exception(str(r.status_code) +
                            ': Comment could not be deleted.')

    def delete(self):
        """ This function deletes this post

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete(self._client.pod + '/posts/' +
                                        self.post_id,
                                        data=data,
                                        headers={'accept': 'application/json'})
