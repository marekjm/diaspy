#!/usr/bin/env python3

"""This module holds functionality related to searching.
"""


class Search():
    """This object is used for searching for content on Diaspora*.
    """
    def __init__(self, connection):
        self._connection = connection

    def lookup_user(self, handle):
        """This function will launch a webfinger lookup from the pod for the
        handle requested. Response code is returned and if the lookup was successful,
        user should soon be searchable via pod used for connection.

        :param string: Handle to search for.
        """
        request = self._connection.get('people', headers={'accept': 'text/html'}, params={'q': handle})
        return request.status_code

    def _query(self, query):
        """Sends search query to pod.

        :param query: search query
        :type query: str
        """
        pass
