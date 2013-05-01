import json
from diaspy.models import Post


class Generic:
    """Object representing generic stream. Used in Tag(), 
    Stream(), Activity() etc.
    """
    def __init__(self, connection, location):
        """
        :param connection: Connection() object
        :param type: diaspy.connection.Connection
        """
        self._connection = connection
        self._location = location
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
        request = self._connection.get(self._location)
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


class Stream(Generic):
    """Object representing user's stream.
    """
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
        return request


class Activity(Generic):
    """Stream representing user's activity.
    """
    pass
