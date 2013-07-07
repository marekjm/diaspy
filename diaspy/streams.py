import json
import time
from diaspy.models import Post, Aspect

"""Docstrings for this module are taken from:
https://gist.github.com/MrZYX/01c93096c30dc44caf71

Documentation for D* JSON API taken from:
http://pad.spored.de/ro/r.qWmvhSZg7rk4OQam
"""


class Generic():
    """Object representing generic stream.
    """
    _location = 'stream.json'
    _stream = []
    #   since epoch
    max_time = int(time.mktime(time.gmtime()))

    def __init__(self, connection, location=''):
        """
        :param connection: Connection() object
        :type connection: diaspy.connection.Connection
        :param location: location of json (optional)
        :type location: str
        """
        self._connection = connection
        if location: self._location = location
        self.fill()

    def __contains__(self, post):
        """Returns True if stream contains given post.
        """
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

    def _obtain(self, max_time=0):
        """Obtains stream from pod.
        """
        params = {}
        if max_time: params['max_time'] = max_time
        request = self._connection.get(self._location, params=params)
        if request.status_code != 200:
            raise error.StreamError('wrong status code: {0}'.format(request.status_code))
        return [Post(self._connection, post['id']) for post in request.json()]

    def _expand(self, new_stream):
        """Appends older posts to stream.
        """
        ids = [post.post_id for post in self._stream]
        stream = self._stream
        for post in new_stream:
            if post.post_id not in ids:
                stream.append(post)
                ids.append(post.post_id)
        self._stream = stream

    def _update(self, new_stream):
        """Updates stream with new posts.
        """
        ids = [post.id for post in self._stream]

        stream = self._stream
        for i in range(len(new_stream)):
            if new_stream[-i].id not in ids:
                stream = [new_stream[-i]] + stream
                ids.append(new_stream[-i].id)
        self._stream = stream

    def clear(self):
        """Removes all posts from stream.
        """
        self._stream = []

    def purge(self):
        """Removes all unexistent posts from stream.
        """
        stream = []
        for post in self._stream:
            deleted = False
            try:
                post.update()
                stream.append(post)
            except Exception:
                deleted = True
            finally:
                if not deleted: stream.append(post)
        self._stream = stream

    def update(self):
        """Updates stream.
        """
        self._update(self._obtain())

    def fill(self):
        """Fills the stream with posts.
        """
        self._stream = self._obtain()

    def more(self, max_time=0):
        """Tries to download more (older ones) Posts from Stream.

        :param max_time: seconds since epoch (optional, diaspy'll figure everything on its own)
        :type max_time: int
        """
        if not max_time: max_time = self.max_time - 3000000
        self.max_time = max_time
        new_stream = self._obtain(max_time=max_time)
        self._expand(new_stream)


class Outer(Generic):
    """Object used by diaspy.models.User to represent
    stream of other user.
    """
    def _obtain(self):
        """Obtains stream of other user.
        """
        request = self._connection.get(self._location)
        if request.status_code != 200:
            raise error.StreamError('wrong status code: {0}'.format(request.status_code))
        return [Post(self._connection, post['id']) for post in request.json()]


class Stream(Generic):
    """The main stream containing the combined posts of the
    followed users and tags and the community spotlights posts
    if the user enabled those.
    """
    location = 'stream.json'

    def post(self, text='', aspect_ids='public', photos=None, photo=''):
        """This function sends a post to an aspect.
        If both `photo` and `photos` are specified `photos` takes precedence.

        :param text: Text to post.
        :type text: str
        :param aspect_ids: Aspect ids to send post to.
        :type aspect_ids: str
        :param photo: filename of photo to post
        :type photo: str
        :param photos: id of photo to post (obtained from _photoupload())
        :type photos: int

        :returns: diaspy.models.Post -- the Post which has been created
        """
        data = {}
        data['aspect_ids'] = aspect_ids
        data['status_message'] = {'text': text}
        if photo: data['photos'] = self._photoupload(photo)
        if photos: data['photos'] = photos

        request = self._connection.post('status_messages',
                                        data=json.dumps(data),
                                        headers={'content-type': 'application/json',
                                                 'accept': 'application/json',
                                                 'x-csrf-token': repr(self._connection)})
        if request.status_code != 201:
            raise Exception('{0}: Post could not be posted.'.format(request.status_code))

        post = Post(self._connection, request.json()['id'])
        return post

    def _photoupload(self, filename):
        """Uploads picture to the pod.

        :param filename: path to picture file
        :type filename: str

        :returns: id of the photo being uploaded
        """
        data = open(filename, 'rb')
        image = data.read()
        data.close()

        params = {}
        params['photo[pending]'] = 'true'
        params['set_profile_image'] = ''
        params['qqfile'] = filename
        aspects = self._connection.getUserInfo()['aspects']
        for i, aspect in enumerate(aspects):
            params['photo[aspect_ids][{0}]'.format(i)] = aspect['id']

        headers = {'content-type': 'application/octet-stream',
                   'x-csrf-token': repr(self._connection),
                   'x-file-name': filename}

        request = self._connection.post('photos', data=image, params=params, headers=headers)
        if request.status_code != 200:
            raise Exception('wrong error code: {0}'.format(request.status_code))
        return request.json()['data']['photo']['id']


class Activity(Stream):
    """Stream representing user's activity.
    """
    _location = 'activity.json'

    def _delid(self, id):
        """Deletes post with given id.
        """
        post = None
        for p in self._stream:
            if p['id'] == id:
                post = p
                break
        if post is not None: post.delete()

    def delete(self, post):
        """Deletes post from users activity.
        `post` can be either post id or Post()
        object which will be identified and deleted.
        After deleting post the stream will be filled.

        :param post: post identifier
        :type post: str, diaspy.models.Post
        """
        if type(post) == str: self._delid(post)
        elif type(post) == Post: post.delete()
        else:
            raise TypeError('this method accepts str or Post types: {0} given')
        self.fill()


class Aspects(Generic):
    """This stream contains the posts filtered by
    the specified aspect IDs. You can choose the aspect IDs with
    the parameter `aspect_ids` which value should be
    a comma seperated list of aspect IDs.
    If the parameter is ommitted all aspects are assumed.
    An example call would be `aspects.json?aspect_ids=23,5,42`
    """
    _location = 'aspects.json'

    def getAspectID(self, aspect_name):
        """Returns id of an aspect of given name.
        Returns -1 if aspect is not found.

        :param aspect_name: aspect name (must be spelled exactly as when created)
        :type aspect_name: str
        :returns: int
        """
        id = -1
        aspects = self._connection.getUserInfo()['aspects']
        for aspect in aspects:
            if aspect['name'] == aspect_name: id = aspect['id']
        return id

    def filterByIDs(self, ids):
        self._location += '?{0}'.format(','.join(ids))
        self.fill()

    def add(self, aspect_name, visible=0):
        """This function adds a new aspect.
        Status code 422 is accepted because it is returned by D* when
        you try to add aspect already present on your aspect list.

        :returns: Aspect() object of just created aspect
        """
        data = {'authenticity_token': self._connection.get_token(),
                'aspect[name]': aspect_name,
                'aspect[contacts_visible]': visible}

        request = self._connection.post('aspects', data=data)
        if request.status_code not in [200, 422]:
            raise Exception('wrong status code: {0}'.format(request.status_code))

        id = self.getAspectID(aspect_name)
        return Aspect(self._connection, id)

    def remove(self, aspect_id=-1, name=''):
        """This method removes an aspect.
        You can give it either id or name of the aspect.
        When both are specified, id takes precedence over name.

        Status code 500 is accepted because although the D* will
        go nuts it will remove the aspect anyway.

        :param aspect_id: id fo aspect to remove
        :type aspect_id: int
        :param name: name of aspect to remove
        :type name: str
        """
        if aspect_id == -1 and name: aspect_id = self.getAspectID(name)
        data = {'_method': 'delete',
                'authenticity_token': self._connection.get_token()}
        request = self._connection.post('aspects/{0}'.format(aspect_id), data=data)
        if request.status_code not in [200, 302, 500]:
            raise Exception('wrong status code: {0}: cannot remove aspect'.format(request.status_code))


class Commented(Generic):
    """This stream contains all posts
    the user has made a comment on.
    """
    _location = 'commented.json'


class Liked(Generic):
    """This stream contains all posts the user liked.
    """
    _location = 'liked.json'


class Mentions(Generic):
    """This stream contains all posts
    the user is mentioned in.
    """
    _location = 'mentions.json'


class FollowedTags(Generic):
    """This stream contains all posts
    containing tags the user is following.
    """
    _location = 'followed_tags.json'

    def remove(self, tag_id):
        """Stop following a tag.

        :param tag_id: tag id
        :type tag_id: int
        """
        data = {'authenticity_token': self._connection.get_token()}
        request = self._connection.delete('tag_followings/{0}'.format(tag_id), data=data)
        if request.status_code != 404:
            raise Exception('wrong status code: {0}'.format(request.status_code))

    def add(self, tag_name):
        """Follow new tag.
        Error code 403 is accepted because pods respod with it when request
        is sent to follow a tag that a user already follows.

        :param tag_name: tag name
        :type tag_name: str
        :returns: int (response code)
        """
        data = {'name': tag_name,
                'authenticity_token': self._connection.get_token(),
                }
        headers = {'content-type': 'application/json',
                   'x-csrf-token': self._connection.get_token(),
                   'accept': 'application/json'
                   }

        request = self._connection.post('tag_followings', data=json.dumps(data), headers=headers)

        if request.status_code not in [201, 403]:
            raise Exception('wrong error code: {0}'.format(request.status_code))
        return request.status_code


class Tag(Generic):
    """This stream contains all posts containing a tag.
    """
    def __init__(self, connection, tag):
        """
        :param connection: Connection() object
        :type connection: diaspy.connection.Connection
        :param tag: tag name
        :type tag: str
        """
        self._connection = connection
        self._location = 'tags/{0}'.format(tag)
        self.fill()
