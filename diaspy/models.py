import requests


class Post:
    """This class represents a post.

    .. note::
        Remember that you need to have access to the post.
        Remember that you also need to be logged in.

    """
    def __init__(self, post_id, client):
        """
        :param post_id: id or guid of the post
        :type post_id: str
        :param client: client object used to authenticate
        :type client: client.Client
        """
        self._client = client
        self.post_id = post_id

    def get_data(self):
        """This function retrieves data of the post.
        """
        r = self._client.session.get('{0}/posts/{1}.json'.format(self._client.pod, self.post_id))
        if r.status_code == 200: 
            return r.json()
        else: 
            raise Exception('wrong status code: {0}'.format(r.status_code))

    def like(self):
        """This function likes a post. 
        It abstracts the 'Like' functionality.

        :returns: dict -- json formatted like object.

        """
        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.post('{0}/posts/{1}/likes'.format(self._client.pod, self.post_id),
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Post could not be liked.'.format(r.status_code))

        return r.json()

    def delete_like(self):
        """This function removes a like from a post

        """
        data = {'authenticity_token': self._client.get_token()}

        post_data = self.get_data()

        r = self._client.session.delete('{0}/posts/{1}/likes/{2}'.format(self._client.pod, self.post_id, post_data['interactions']['likes'][0]['id']),
                                        data=data)

        if r.status_code != 204:
            raise Exception('{0}: Like could not be removed.'.format(r.status_code))

    def reshare(self):
        """This function reshares a post

        """
        post_data = self.get_data()

        data = {'root_guid': post_data['guid'],
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post('{0}/reshares'.format(self._client.pod),
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Post could not be reshared.'.format(r.status_code))

        return r.json()

    def comment(self, text):
        """This function comments on a post

        :param text: text to comment.
        :type text: str

        """
        data = {'text': text,
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post('{0}/posts/{1}/comments'.format(self._client.pod, self.post_id),
                                      data=data,
                                      headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception('{0}: Comment could not be posted.'.format(r.status_code))

        return r.json()

    def delete_comment(self, comment_id):
        """This function removes a comment from a post

        :param comment_id: id of the comment to remove.
        :type comment_id: str

        """
        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete('{0}/posts/{1}/comments/{2}'.format(self._client.pod, self.post_id, comment_id),
                                        data=data,
                                        headers={'accept': 'application/json'})

        if r.status_code != 204:
            raise Exception('{0}: Comment could not be deleted.'.format(r.status_code))

    def delete(self):
        """ This function deletes this post

        """
        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete('{0}/posts/{1}'.format(self._client.pod, self.post_id),
                                        data=data,
                                        headers={'accept': 'application/json'})
