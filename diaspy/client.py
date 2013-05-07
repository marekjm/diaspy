import diaspy.models
import diaspy.streams
import diaspy.connection


class Client:
    """This is the client class used to interact with Diaspora.
    It can be used as a reference implementation of client using diaspy.
    """
    def __init__(self, pod, username='', password=''):
        """
        `pod` can also be a diaspy.connection.Connection type and
        Client() will detect it. When giving a connection there is no need 
        to pass username and password.

        :param pod: The complete url of the diaspora pod to use
        (or Connection() object).
        :type pod: str
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str
        """
        if type(pod) == diaspy.connection.Connection:
            self.connection = pod
        else:
            self.connection = diaspy.connection.Connection(pod, username, password)
            self.connection.login()
        self.stream = diaspy.streams.Stream(self.connection, 'stream.json')

    def post(self, text, aspect_ids='public', photos=None, photo=''):
        """This function sends a post to an aspect

        :param text: text to post
        :type text: str
        :param aspect_ids: Aspect ids to send post to.
        :type aspect_ids: str
        :param photo: path to picture file
        :type photo: str
 
        :returns: diaspy.models.Post -- the Post which has been created
        """
        post = self.stream.post(text, aspect_ids, photos, photo)
        return post

    def get_activity(self):
        """This function returns activity stream.

        :returns: diaspy.streams.Activity
        """
        activity = diaspy.streams.Activity(self.connection, 'activity.json')
        return activity

    def get_stream(self):
        """This functions returns stream.

        :returns: diaspy.streams.Stream
        """
        self.stream.update()
        return self.stream

    def get_aspects(self):
        """Returns aspects stream.

        :returns: diaspy.streams.Aspects
        """
        return diaspy.streams.Aspects(self.connection)

    def get_mentions(self):
        """Returns /mentions stream.

        :returns: diaspy.streams.Mentions
        """
        return diaspy.streams.Mentions(self.connection)

    def get_followed_tags(self):
        """Returns followed tags stream.

        :returns: diaspy.streams.FollowedTags
        """
        return diaspy.streams.FollowedTags(self.connection)

    def get_tag(self, tag):
        """This functions returns a list of posts containing the tag.
        :param tag: Name of the tag
        :type tag: str

        :returns: diaspy.streams.Generic -- stream containg posts with given tag
        """
        return diaspy.streams.Generic(self.connection, location='tags/{0}.json'.format(tag))

    def get_notifications(self):
        """This functions returns a list of notifications.

        :returns: list -- list of json formatted notifications
        """
        r = self.connection.get('notifications.json')

        if r.status_code != 200:
            raise Exception('wrong status code: {0}'.format(r.status_code))

        notifications = r.json()
        return notifications

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

    def add_aspect(self, aspect_name, visible=0):
        """This function adds a new aspect.
        """
        diaspy.streams.Aspects(self.connection).add(aspect_name, visible)

    def remove_aspect(self, aspect_id):
        """This function removes an aspect.
        """
        diaspy.streams.Aspects(self.connection).remove(aspect_id)

    def add_user_to_aspect(self, user_id, aspect_id):
        """ this function adds a user to an aspect.

        :param user_id: User ID
        :type user_id: str
        :param aspect_id: Aspect ID
        :type aspect_id: str

        """
        return diaspy.models.Aspect(self.connection, aspect_id).addUser(user_id)

    def remove_user_from_aspect(self, user_id, aspect_id):
        """ this function removes a user from an aspect.

        :param user_id: User ID
        :type user_id: str
        :param aspect_id: Aspect ID
        :type aspect_id: str

        """
        return diaspy.models.Aspect(self.connection, aspect_id).removeUser(user_id)

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
                'authenticity_token': self.connection.get_token()}

        r = self.connection.post('conversations/',
                                 data=data,
                                 headers={'accept': 'application/json'})
        if r.status_code != 200:
            raise Exception('{0}: Conversation could not be started.'
                            .format(r.status_code))
        return r.json()
