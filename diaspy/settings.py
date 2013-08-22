"""This module provides access to user's settings on Diaspora*.
"""


import json
import re
import urllib

from diaspy import errors


class Settings():
    """This object is used to get access to user's settings on
    Diaspora* and provides interface for downloading user's stuff.
    """
    def __init__(self, connection):
        self._connection = connection
    
    def downloadxml(self):
        request = self._connection.get('user/export')
        return request.text

    def setEmail(self, email):
        """Changes user's email.
        """
        data = {'_method': 'put', 'utf-8': '✓', 'user[email]': email, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user')

    def getEmail(self):
        """Returns currently used email.
        """
        data = self._connection.get('user/edit')
        email = re.compile('<input id="user_email" name="user\[email\]" size="30" type="text" value=".+?"').search(data.text)
        if email is None: raise errors.DiaspyError('cannot fetch email')
        email = email.group(0)[:-1]
        email = email[email.rfind('"')+1:]
        return email

    def setLanguage(self, lang):
        """Changes user's email.
        """
        data = {'_method': 'put', 'utf-8': '✓', 'user[language]': lang, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user')

    def getLanguages(self):
        """Returns a list of tuples containing ('Language name', 'identifier').
        One of the Black Magic(tm) methods.
        """
        select_start = '<select id="user_language" name="user[language]">'
        select_end = '</select>'
        languages = []
        request = self._connection.get('user/edit')
        data = request.text[request.text.find(select_start)+len(select_start):]
        data = data[:data.find(select_end)].split('\n')
        for item in data:
            name = item[item.find('>')+1:item.rfind('<')]
            identifier = item[item.find('"')+1:]
            identifier = identifier[:identifier.find('"')]
            languages.append((name, identifier))
        return languages
