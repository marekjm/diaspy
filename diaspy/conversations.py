#!/usr/bin/env python3


class Conversation:
    """This class represents a conversation.

    .. note::
        Remember that you need to have access to the conversation.

    """
    def __init__(self, conv_id, client):
        """
        :param conv_id: id of the post and not the guid!
        :type conv_id: str
        :param client: client object used to authenticate
        :type client: client.Client

        .. note::
            The login function of the client should be called,
            before calling any of the post functions.

        """
        self._client = client
        self.conv_id = conv_id

    def get_data(self):
        """ returns the plain json data representing conversation.
        """
        r = self._client._sessionget('conversations/{1}.json'.format(self.conv_id))
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
                'authenticity_token': self._client.get_token()}

        r = self._client._sessionpost('conversations/{}/messages'.format(self.conv_id),
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
        data = {'authenticity_token': self._client.get_token()}

        r = self._client.session.delete('{0}/conversations/{1}/visibility/'
                                        .format(self._client.pod,
                                                self.conv_id),
                                        data=data,
                                        headers={'accept': 'application/json'})

        if r.status_code != 404:
            raise Exception('{0}: Conversation could not be deleted.'
                            .format(r.status_code))

    def get_subject(self):
        """ return the subject of this conversation
        """
        return self.get_data()['subject']
