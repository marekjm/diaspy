#!/usr/bin/env python3


class Conversation():
    """This class represents a conversation.

    .. note::
        Remember that you need to have access to the conversation.
    """
    def __init__(self, conv_id, connection):
        """
        :param conv_id: id of the post and not the guid!
        :type conv_id: str
        :param connection: connection object used to authenticate
        :type connection: connection.Connection

        .. note::
            The login function of the connection should be called,
            before calling any of the post functions.

        """
        self._connection = connection
        self.conv_id = conv_id

    def get_data(self):
        """ returns the plain json data representing conversation.
        """
        r = self._connection.get('conversations/{1}.json'.format(self.conv_id))
        if r.status_code == 200:
            return r.json()['conversation']
        else:
            raise Exception('wrong status code: {0}'.format(r.status_code))

    def answer(self, text):
        """ answer that conversation

        :param text: text to answer.
        :type text: str

        """

        data = {'message[text]': text,
                'utf8': '&#x2713;',
                'authenticity_token': self._connection.get_token()}

        r = self._connection.post('conversations/{}/messages'.format(self.conv_id),
                                  data=data,
                                  headers={'accept': 'application/json'})
        if r.status_code != 200:
            raise Exception('{0}: Answer could not be posted.'
                            .format(r.status_code))
        return r.json()

    def delete(self):
        """ delete this conversation
            has to be implemented
        """
        data = {'authenticity_token': self._connection.get_token()}

        r = self._connection.delete('conversations/{0}/visibility/'
                                    .format(self.conv_id),
                                    data=data,
                                    headers={'accept': 'application/json'})

        if r.status_code != 404:
            raise Exception('{0}: Conversation could not be deleted.'
                            .format(r.status_code))

    def get_subject(self):
        """ return the subject of this conversation
        """
        return self.get_data()['subject']
