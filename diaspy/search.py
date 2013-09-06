#!/usr/bin/env python3

"""This module holds functionality related to searching.
"""


from diaspy import errors


class Search():
    """This object is used for searching for content on Diaspora*.
    """
    def __init__(self, connection):
        self._connection = connection

    def lookupUser(self, handle):
        """This function will launch a webfinger lookup from the pod for the
        handle requested. Response code is returned and if the lookup was successful,
        user should soon be searchable via pod used for connection.

        :param string: Handle to search for.
        """
        request = self._connection.get('people', headers={'accept': 'text/html'}, params={'q': handle})
        return request.status_code

    def user(self, query):
        """Searches for a user.
        Will return list of dictionaries containing
        data of found users.
        """
        request = self._connection.get('people.json', params={'q': query, 'utf-8': '%u2713'})
        if request.status_code != 200:
            raise errors.SearchError('wrong status code: {0}'.format(request.status_code))
        return request.json()

    def tags(self, query, limit=10):
        """Retrieve tag suggestions.

        :param query: query used to search
        :type query: str
        :param limit: maxmal number of suggestions returned
        :type limit: int
        """
        params = {'q': query, 'limit': limit}
        request = self._connection.get('tags', params=params, headers={'x-csrf-token': repr(self._connection)})
        if request.status_code != 200:
            raise errors.SearchError('wrong status code: {0}'.format(request.status_code))
        return [i['name'] for i in request.json()]
