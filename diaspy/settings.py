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

    def changeEmail(self, email):
        """Changes user's email.
        """
        data = {'_method': 'put', 'utf-8': '✓', 'user[email]': email, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user')

    def changeLanguage(self, lang):
        """Changes user's email.
        """
        data = {'_method': 'put', 'utf-8': '✓', 'user[language]': lang, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user')

    def getLanguages(self):
        """Returns a list of tuples containing ('Language name', 'identifier').
        One of the Black Magic(tm) methods.
        """
        select_start = '<select id="user_language" name="user[language]"')
        select_end = '</select>'
        languages = []
        request = self._connection.get('user/edit')
        data = request.text[request.text.find(select_start):]
        data = data[:data.find(select_end)]
        print(data)
        return languages
