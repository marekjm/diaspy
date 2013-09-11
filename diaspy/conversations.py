#!/usr/bin/env python3


from diaspy import errors, models


class Mailbox():
    """Object implementing diaspora* mailbox.
    """
    def __init__(self, connection, fetch=True):
        self._connection = connection
        self._mailbox = []
        if fetch: self._fetch()

    def __len__(self):
        return len(self._mailbox)

    def __iter__(self):
        return iter(self._mailbox)

    def __getitem__(self, n):
        return self._mailbox[n]

    def _fetch(self):
        """This method will fetch messages from user's mailbox.
        """
        request = self._connection.get('conversations.json')

        if request.status_code != 200:
            raise errors.DiaspyError('wrong status code: {0}'.format(request.status_code))
        mailbox = request.json()
        self._mailbox = [models.Conversation(self._connection, c['conversation']['id']) for c in mailbox]
