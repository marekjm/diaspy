import requests

class Conversation:
    """This class represents a conversation.

    .. note::
        Remember that you need to have access to the conversation.

    """

    def __init__(self, conv_id, client):
        """
        :param conversation_id: id of the post and not the guid!
        :type conversation_id: str
        :param client: client object used to authenticate
        :type client: client.Client

        .. note::
            The login function of the client should be called,
            before calling any of the post functions.

        """
        self._client = client
        self.conv_id = conv_id

    def get_data(self):
        """ returns the plain json data
        """
        r = self._client.session.get(self._client.pod +
                                     '/conversations/' +
                                     self.conv_id +
                                     '.json')
        if r.status_code == 200:
            return r.json()['conversation']
        else:
            raise Exception('wrong status code: ' + str(r.status_code))

    def answer(self, text):
        """ answer that conversation

        :param text: text to answer.
        :type text: str

        """

        data = {'message[text]': text,
                'utf8': '&#x2713;',
                'authenticity_token': self._client.get_token()}

        r = self._client.session.post(self._client.pod +
                                      '/conversations/' +
                                      self.conv_id +
                                      '/messages',
                                      data=data,
                                      headers={'accept': 'application/json'})
        if r.status_code != 200:
            raise Exception(str(r.status_code) +
                            ': Answer could not be posted.')

        return r.json()

    def delete(self):
        """ delete this conversation
            has to be implemented
        """
        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete(self._client.pod + '/conversations/' +
                                        self.conv_id +
                                        '/visibility/',
                                        data=data,
                                        headers={'accept': 'application/json'})

        if r.status_code != 404:
            raise Exception(str(r.status_code) +
                            ': Conversation could not be deleted.')

    def get_subject(self):
        """ return the subject of this conversation
        """
        return self.get_data()['subject']
