import re
import json
import diaspy.models
import diaspy.connection


class Client:
    """This is the client class to connect to Diaspora.
    """
    def __init__(self, pod, username, password):
        """
        :param pod: The complete url of the diaspora pod to use.
        :type pod: str
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str
        """
        self.connection = diaspy.connection.Connection(pod, username, password)
        self.connection.login()
        self.pod = pod

    def _setpostdata(self, text, aspect_ids, photos):
        """This function prepares data for posting.

        :param text: Text to post.
        :type text: str
        :param aspect_ids: Aspect ids to send post to.
        :type aspect_ids: str
        """
        data = {}
        data['aspect_ids'] = aspect_ids
        data['status_message'] = {'text': text}
        if photos:
            data['photos'] = photos
        self._post_data = data

    def _post(self):
        """Sends post to an aspect.

        :returns: diaspy.models.Post -- the Post which has been created
        """
        r = self.connection.post('status_messages',
                                 data=json.dumps(self._post_data),
                                 headers={'content-type': 'application/json',
                                          'accept': 'application/json',
                                          'x-csrf-token': self.get_token()})
        if r.status_code != 201:
            raise Exception('{0}: Post could not be posted.'.format(
                            r.status_code))

        return diaspy.models.Post(str(r.json()['id']), self.connection)

    def post(self, text, aspect_ids='public', photos=None):
        """This function sends a post to an aspect

        :param text: Text to post.
        :type text: str
        :param aspect_ids: Aspect ids to send post to.
        :type aspect_ids: str

        :returns: diaspy.models.Post -- the Post which has been created
        """
        self._setpostdata(text, aspect_ids, photos)
        post = self._post()
        self._post_data = {}
        return post

    def get_user_info(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.
        """
        r = self.connection.get('bookmarklet')
        regex = re.compile(r'window.current_user_attributes = ({.*})')
        userdata = json.loads(regex.search(r.text).group(1))
        return userdata

    def post_picture(self, filename):
        """This method posts a picture to D*.

        :param filename: Path to picture file.
        :type filename: str
        """
        aspects = self.get_user_info()['aspects']
        params = {}
        params['photo[pending]'] = 'true'
        params['set_profile_image'] = ''
        params['qqfile'] = filename
        for i, aspect in enumerate(aspects):
            params['photo[aspect_ids][%d]' % (i)] = aspect['id']

        data = open(filename, 'rb')

        headers = {'content-type': 'application/octet-stream',
                   'x-csrf-token': self.get_token(),
                   'x-file-name': filename}

        r = self.connection.post('photos', params=params, data=data, headers=headers)
        return r

    def get_stream(self):
        """This functions returns a list of posts found in the stream.

        :returns: list -- list of Post objects.
        """
        request = self.connection.get('stream.json')

        if request.status_code != 200:
            raise Exception('wrong status code: {0}'.format(request.status_code))

        stream = request.json()
        return [diaspy.models.Post(str(post['id']), self.connection) for post in stream]

    def get_notifications(self):
        """This functions returns a list of notifications.

        :returns: list -- list of json formatted notifications
        """
        r = self.connection.get('notifications.json')

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        notifications = r.json()
        return notifications

    def get_mentions(self):
        """This functions returns a list of
        posts the current user is being mentioned in.

        :returns: list -- list of Post objects
        """
        r = self.connection.get('mentions.json')

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        mentions = r.json()
        return [diaspy.models.Post(str(post['id']), self.connection) for post in mentions]

    def get_tag(self, tag):
        """This functions returns a list of posts containing the tag.
        :param tag: Name of the tag
        :type tag: str

        :returns: list -- list of Post objects
        """
        r = self.connection.get('tags/{0}.json'.format(tag))

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        tagged_posts = r.json()
        return [diaspy.models.Post(str(post['id']), self.connection) for post in tagged_posts]

    def get_mailbox(self):
        """This functions returns a list of messages found in the conversation.

        :returns: list -- list of Conversation objects.
        """
        r = self.connection.get('conversations.json')

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        mailbox = r.json()
        return [diaspy.conversations.Conversation(str(conversation['conversation']['id']), self.connection)
                for conversation in mailbox]

    def add_user_to_aspect(self, user_id, aspect_id):
        """ this function adds a user to an aspect.

        :param user_id: User ID
        :type user_id: str
        :param aspect_id: Aspect ID
        :type aspect_id: str

        """
        data = {'authenticity_token': self.get_token(),
                'aspect_id': aspect_id,
                'person_id': user_id}

        r = self.connection.post('aspect_memberships.json', data=data)

        if r.status_code != 201:
            raise Exception('wrong status code: {0}'.format(r.status_code))
        return r.json()

    def add_aspect(self, aspect_name, visible=0):
        """ This function adds a new aspect.
        """

        data = {'authenticity_token': self.get_token(),
                'aspect[name]': aspect_name,
                'aspect[contacts_visible]': visible}

        r = self.connection.post('aspects', data=data)

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

    def remove_user_from_aspect(self, user_id, aspect_id):
        """ this function removes a user from an aspect.

        :param user_id: User ID
        :type user_id: str
        :param aspect_id: Aspect ID
        :type aspect_id: str

        """
        data = {'authenticity_token': self.get_token(),
                'aspect_id': aspect_id,
                'person_id': user_id}

        r = self.connection.delete('aspect_memberships/42.json',
                                   data=data)

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        return r.json()

    def remove_aspect(self, aspect_id):
        """ This function adds a new aspect.
        """
        data = {'authenticity_token': self.get_token()}

        r = self.connection.delete('aspects/{}'.format(aspect_id),
                                   data=data)

        if r.status_code != 404:
            raise Exception('wrong status code: {0}'.format(r.status_code))

    def new_conversation(self, contacts, subject, text):
        """Start a new conversation.

        :param contacts: recipients ids, no guids, comma sperated.
        :type contacts: str
        :param subject: subject of the message.
        :type subject: str
        :param text: text of the message.
        :type text: str
        """
        data = {'contact_ids': contacts,
                'conversation[subject]': subject,
                'conversation[text]': text,
                'utf8': '&#x2713;',
                'authenticity_token': self.connection.getToken()}

        r = self.connection.post('conversations/',
                                 data=data,
                                 headers={'accept': 'application/json'})
        if r.status_code != 200:
            raise Exception('{0}: Conversation could not be started.'
                            .format(r.status_code))
        return r.json()
