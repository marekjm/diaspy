import json
import re
import urllib


"""This module provides access to user's settings on Diaspora*.
"""


class Settings():
    """This object is used to get access to user's settings on
    Diaspora* and provides interface for downloading user's stuff.
    """
    def __init__(self, connection):
        self._connection = connection
    
    def downloadxml(self):
        request = self._connection.get('user/export')
        return request.text

