#!/usr/bin/env python3


import json


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


class Stream:
    """Object representing user's stream.
    """
    def __init__(self, connection):
        """
        :param connection: Connection() object
        :param type: diaspy.connection.Connection
        """
        self._connection = connection
        self._stream = []
        self.fill()

    def __contains__(self, post):
        """Returns True if stream contains given post.
        """
        if type(post) is not Post:
            raise TypeError('stream can contain only posts: checked for {0}'.format(type(post)))
        return post in self._stream

    def __iter__(self):
        """Provides iterable interface for stream.
        """
        return iter(self._stream)

    def __getitem__(self, n):
        """Returns n-th item in Stream.
        """
        return self._stream[n]

    def __len__(self):
        """Returns length of the Stream.
        """
        return len(self._stream)

    def _obtain(self):
        """Obtains stream from pod.
        """
        request = self._connection.get('stream.json')
        if request.status_code != 200:
            raise Exception('wrong status code: {0}'.format(request.status_code))
        return [Post(str(post['id']), self._connection) for post in request.json()]

    def clear(self):
        """Removes all posts from stream.
        """
        self._stream = []

    def update(self):
        """Updates stream.
        """
        stream = self._obtain()
        _stream = self._stream
        for i in range(len(stream)):
            if stream[-i] not in _stream:
                _stream = [stream[-i]] + _stream
        self._stream = _stream

    def fill(self):
        """Fills the stream with posts.
        """
        self._stream = self._obtain()

    def post(self, text, aspect_ids='public', photos=None):
        """This function sends a post to an aspect

        :param text: Text to post.
        :type text: str
        :param aspect_ids: Aspect ids to send post to.
        :type aspect_ids: str

        :returns: diaspy.models.Post -- the Post which has been created
        """
        data = {}
        data['aspect_ids'] = aspect_ids
        data['status_message'] = {'text': text}
        if photos: data['photos'] = photos
        request = self._connection.post('status_messages',
                                        data=json.dumps(data),
                                        headers={'content-type': 'application/json',
                                                 'accept': 'application/json',
                                                 'x-csrf-token': self._connection.getToken()})
        if request.status_code != 201:
            raise Exception('{0}: Post could not be posted.'.format(
                            request.status_code))

        post = Post(str(request.json()['id']), self._connection)
        self.update()
        return post

    def post_picture(self, filename):
        """This method posts a picture to D*.

        :param filename: Path to picture file.
        :type filename: str
        """
        aspects = self._connection.getUserInfo()['aspects']
        params = {}
        params['photo[pending]'] = 'true'
        params['set_profile_image'] = ''
        params['qqfile'] = filename
        for i, aspect in enumerate(aspects):
            params['photo[aspect_ids][%d]' % (i)] = aspect['id']

        data = open(filename, 'rb')

        headers = {'content-type': 'application/octet-stream',
                   'x-csrf-token': self._connection.getToken(),
                   'x-file-name': filename}
        request = self._connection.post('photos', params=params, data=data, headers=headers)
        data.close()
        self.update()
        return request
