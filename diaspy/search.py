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
        handle requested. Nothing is returned but if the lookup was successful,
        user should soon be searchable via this pod.
        
        :param string: Handle to search for.
        """
        request = self.get('people', headers={'accept': 'text/html'}, params={'q':handle})
