#!/usr/bin/env python3


from diaspy import errors


class Conversation():
    """This class represents a conversation.

    .. note::
        Remember that you need to have access to the conversation.
    """
    def __init__(self, connection, id, fetch=True):
        """
        :param conv_id: id of the post and not the guid!
        :type conv_id: str
        :param connection: connection object used to authenticate
        :type connection: connection.Connection
        """
        self._connection = connection
        self.id = id
        self.data = {}
        if fetch: self._fetch()

    def _fetch(self):
        """Fetches JSON data representing conversation.
        """
        request = self._connection.get('conversations/{}.json'.format(self.id))
        if request.status_code == 200:
            self.data = request.json()['conversation']
        else:
            raise errors.ConversationError('cannot download conversation data: {0}'.format(request.status_code))

    def answer(self, text):
        """Answer that conversation

        :param text: text to answer.
        :type text: str
        """
        data = {'message[text]': text,
                'utf8': '&#x2713;',
                'authenticity_token': repr(self._connection)}

        request = self._connection.post('conversations/{}/messages'.format(self.id),
                                        data=data,
                                        headers={'accept': 'application/json'})
        if request.status_code != 200:
            raise errors.ConversationError('{0}: Answer could not be posted.'
                            .format(request.status_code))
        return request.json()

    def delete(self):
        """Delete this conversation.
        Has to be implemented.
        """
        data = {'authenticity_token': repr(self._connection)}

        request = self._connection.delete('conversations/{0}/visibility/'
                                    .format(self.id),
                                    data=data,
                                    headers={'accept': 'application/json'})

        if request.status_code != 404:
            raise errors.ConversationError('{0}: Conversation could not be deleted.'
                            .format(request.status_code))

    def get_subject(self):
        """Returns the subject of this conversation
        """
        return self.data['subject']
