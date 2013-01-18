import requests


class Post:
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.

    :params post_id: id or guid of the post
    :type post_id: str
    :params client: client object used to authenticate
    :type client: Client

    .. note::
        The login function of the client should be called,
        before calling any of the post functions.

    """

    def __init__(self, post_id, client):

        self._client = client
        r = self._client.session.get(self._client.pod +
                                     '/posts/' +
                                     post_id +
                                     '.json')
        if r.status_code == 200:
            self.data = r.json()
        else:
            raise Exception('wrong status code: ' + str(r.status_code))

    def like(self):
        """This function likes a post

        :returns: dict -- json formatted like object.

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      "/posts/" +
                                      str(self.data['id']) +
                                      "/likes",
                                      data=data,
                                      headers={'accept': 'application/json'})
        return r.json()

    def rmlike(self):
        """This function removes a like from a post

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete(self._client.pod + '/posts/' +
                                        str(self.data['id']) +
                                        '/likes/' +
                                        str(self.data['interactions']
                                            ['likes'][0]['id']),
                                        data=data)

    def reshare(self):
        """This function reshares a post

        """

        data = {'root_guid': self.data['guid'],
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      "/reshares",
                                      data=data)

        return r.json()

    def comment(self, text):
        """This function comments on a post

        :param post_id: id of the post to comment on.
        :type post_id: str
        :param text: text to comment.
        :type text: str

        """

        data = {'text': text,
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      '/posts/' +
                                      str(self.data['id']) +
                                      '/comments',
                                      data=data)

        return r.json()

    def rmcomment(self, comment_id):
        """This function removes a comment from a post

        :param post_id: id of the post to remove the like from.
        :type post_id: str
        :param like_id: id of the like to remove.
        :type like_id: str

        """

        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete(self._client.pod + '/posts/' +
                                        str(self.data['id']) +
                                        '/comments/' +
                                        comment_id,
                                        data=data)
