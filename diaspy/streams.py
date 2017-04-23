"""Docstrings for this module are taken from:
https://gist.github.com/MrZYX/01c93096c30dc44caf71

Documentation for D* JSON API taken from:
http://pad.spored.de/ro/r.qWmvhSZg7rk4OQam
"""


import json
import time
from diaspy.models import Post, Aspect
from diaspy import errors


class Generic():
    """Object representing generic stream.
    """
    _location = 'stream.json'

    def __init__(self, connection, location='', fetch=True):
        """
        :param connection: Connection() object
        :type connection: diaspy.connection.Connection
        :param location: location of json (optional)
        :type location: str
        :param fetch: will call .fill() if true
        :type fetch: bool
        """
        self._connection = connection
        if location: self._location = location
        self._stream = []
        #   since epoch
        self.max_time = int(time.mktime(time.gmtime()))
        if fetch: self.fill()

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

    def _obtain(self, max_time=0, suppress=True):
        """Obtains stream from pod.

        suppress:bool - suppress post-fetching errors (e.g. 404)
        """
        params = {}
        if max_time:
            params['max_time'] = max_time
            params['_'] = int(time.time() * 1000)
        request = self._connection.get(self._location, params=params)
        if request.status_code != 200:
            raise errors.StreamError('wrong status code: {0}'.format(request.status_code))
        posts = []
        for post in request.json():
            try:
                posts.append(Post(self._connection, guid=post['guid']))
            except errors.PostError:
                if not suppress:
                    raise
        return posts

    def _expand(self, new_stream):
        """Appends older posts to stream.
        """
        ids = [post.id for post in self._stream]
        stream = self._stream
        for post in new_stream:
            if post.id not in ids:
                stream.append(post)
                ids.append(post.id)
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
        """Set stream to empty.
        """
        self._stream = []

    def purge(self):
        """Removes all unexistent posts from stream.
        """
        stream = []
        for post in self._stream:
            deleted = False
            try:
                # error will tell us that the post has been deleted
                post.update()
            except Exception:
                deleted = True
            finally:
                if not deleted: stream.append(post)
        self._stream = stream

    def update(self):
        """Updates stream with new posts.
        """
        self._update(self._obtain())

    def fill(self):
        """Fills the stream with posts.

        **Notice:** this will create entirely new list of posts.
        If you want to preseve posts already present in stream use update().
        """
        self._stream = self._obtain()

    def more(self, max_time=0, backtime=84600):
        """Tries to download more (older posts) posts from Stream.

        :param backtime: how many seconds substract each time (defaults to one day)
        :type backtime: int
        :param max_time: seconds since epoch (optional, diaspy'll figure everything on its own)
        :type max_time: int
        """
        if not max_time: max_time = self.max_time - backtime
        self.max_time = max_time
        new_stream = self._obtain(max_time=max_time)
        self._expand(new_stream)

    def full(self, backtime=84600, retry=42, callback=None):
        """Fetches full stream - containing all posts.
        WARNING: this is a **VERY** long running function.
        Use callback parameter to access information about the stream during its
        run.

        Default backtime is one day. But sometimes user might not have any activity for longer
        period (in the beginning of my D* activity I was posting once a month or so).
        The role of retry is to hadle such situations by trying to go further back in time.
        If a post is found the counter is restored.

        Default retry is 42. If you don't know why go to the nearest library (or to the nearest
        Piratebay mirror) and grab a copy of "A Hitchhiker's Guide to the Galaxy" and read the
        book to find out. This will also increase your level of geekiness and you'll have a
        great time reading the book.

        :param backtime: how many seconds to substract each time
        :type backtime: int
        :param retry: how many times the functin should look deeper than your last post
        :type retry: int
        :param callback: callable taking diaspy.streams.Generic as an argument
        :returns: integer, lenght of the stream
        """
        oldstream = self.copy()
        self.more()
        while len(oldstream) < len(self):
            oldstream = self.copy()
            if callback is not None: callback(self)
            self.more(backtime=backtime)
            if len(oldstream) < len(self): continue
            # but if no posts were found start retrying...
            print('retrying... {0}'.format(retry))
            n = retry
            while n > 0:
                print('\t', n, self.max_time)
                # try to get even more posts...
                self.more(backtime=backtime)
                print('\t', len(oldstream), len(self))
                # check if it was a success...
                if len(oldstream) < len(self):
                    # and if so restore normal order of execution by
                    # going one loop higher
                    break
                oldstream = self.copy()
                # if it was not a success substract one backtime, keep calm and
                # try going further back in time...
                n -= 1
            # check the comment below
            # no commented code should be present in good software
            #if len(oldstream) == len(self): break
        return len(self)

    def copy(self):
        """Returns copy (list of posts) of current stream.
        """
        return [p for p in self._stream]

    def json(self, comments=False, **kwargs):
        """Returns JSON encoded string containing stream's data.

        :param comments: to include comments or not to include 'em, that is the question this param holds answer to
        :type comments: bool
        """
        stream = [post for post in self._stream]
        if comments:
            for i, post in enumerate(stream):
                post._fetchcomments()
                comments = [c.data for c in post.comments]
                post['interactions']['comments'] = comments
                stream[i] = post
        stream = [post._data for post in stream]
        return json.dumps(stream, **kwargs)


class Outer(Generic):
    """Object used by diaspy.models.User to represent
    stream of other user.
    """
    def __init__(self, connection, guid, fetch=True):
        location = 'people/{}/stream.json'.format(guid)
        super().__init__(connection, location, fetch)

    def _obtain(self, max_time=0):
        """Obtains stream from pod.
        """
        params = {}
        if max_time: params['max_time'] = max_time
        request = self._connection.get(self._location, params=params)
        if request.status_code != 200:
            raise errors.StreamError('wrong status code: {0}'.format(request.status_code))
        return [Post(self._connection, post['id']) for post in request.json()]


class Stream(Generic):
    """The main stream containing the combined posts of the
    followed users and tags and the community spotlights posts
    if the user enabled those.
    """
    location = 'stream.json'

    def post(self, text='', aspect_ids='public', photos=None, photo='', provider_display_name=''):
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
        :param provider_display_name: name of provider displayed under the post
        :type provider_display_name: str

        :returns: diaspy.models.Post -- the Post which has been created
        """
        data = {}
        data['aspect_ids'] = aspect_ids
        data['status_message'] = {'text': text, 'provider_display_name': provider_display_name}
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

    def _photoupload(self, filename, aspects=[]):
        """Uploads picture to the pod.

        :param filename: path to picture file
        :type filename: str
        :param aspect_ids: list of ids of aspects to which you want to upload this photo
        :type aspect_ids: list of integers

        :returns: id of the photo being uploaded
        """
        data = open(filename, 'rb')
        image = data.read()
        data.close()

        params = {}
        params['photo[pending]'] = 'true'
        params['set_profile_image'] = ''
        params['qqfile'] = filename
        if not aspects: aspects = self._connection.getUserData()['aspects']
        for i, aspect in enumerate(aspects):
            params['photo[aspect_ids][{0}]'.format(i)] = aspect['id']

        headers = {'content-type': 'application/octet-stream',
                   'x-csrf-token': repr(self._connection),
                   'x-file-name': filename}

        request = self._connection.post('photos', data=image, params=params, headers=headers)
        if request.status_code != 200:
            raise errors.StreamError('photo cannot be uploaded: {0}'.format(request.status_code))
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
        After deleting post the stream will be purged.

        :param post: post identifier
        :type post: str, diaspy.models.Post
        """
        if type(post) == str: self._delid(post)
        elif type(post) == Post: post.delete()
        else: raise TypeError('this method accepts str or Post types: {0} given')
        self.purge()


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
        aspects = self._connection.getUserData()['aspects']
        for aspect in aspects:
            if aspect['name'] == aspect_name: id = aspect['id']
        return id

    def filter(self, ids):
        """Filters posts by given aspect ids.

        :parameter ids: list of apsect ids
        :type ids: list of integers
        """
        self._location = 'aspects.json' + '?{0}'.format(','.join(ids))
        self.fill()

    def add(self, aspect_name, visible=0):
        """This function adds a new aspect.
        Status code 422 is accepted because it is returned by D* when
        you try to add aspect already present on your aspect list.

        :param aspect_name: name of aspect to create
        :param visible: whether the contacts in this aspect are visible to each other or not

        :returns: Aspect() object of just created aspect
        """
        data = {'authenticity_token': repr(self._connection),
                'aspect[name]': aspect_name,
                'aspect[contacts_visible]': visible}

        request = self._connection.post('aspects', data=data)
        if request.status_code not in [200, 422]:
            raise Exception('wrong status code: {0}'.format(request.status_code))

        id = self.getAspectID(aspect_name)
        return Aspect(self._connection, id)

    def remove(self, id=-1, name=''):
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
        if id == -1 and name: id = self.getAspectID(name)
        data = {'_method': 'delete',
                'authenticity_token': repr(self._connection)}
        request = self._connection.post('aspects/{0}'.format(id), data=data)
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

    def get(self):
        """Returns list of followed tags.
        """
        return []

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
                'authenticity_token': repr(self._connection),
                }
        headers = {'content-type': 'application/json',
                   'x-csrf-token': repr(self._connection),
                   'accept': 'application/json'
                   }

        request = self._connection.post('tag_followings', data=json.dumps(data), headers=headers)

        if request.status_code not in [201, 403]:
            raise Exception('wrong error code: {0}'.format(request.status_code))
        return request.status_code


class Tag(Generic):
    """This stream contains all posts containing a tag.
    """
    def __init__(self, connection, tag, fetch=True):
        """
        :param connection: Connection() object
        :type connection: diaspy.connection.Connection
        :param tag: tag name
        :type tag: str
        """
        self._connection = connection
        self._location = 'tags/{0}.json'.format(tag)
        if fetch: self.fill()
