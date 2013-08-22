"""This module provides access to user's settings on Diaspora*.
"""


import json
import os
import re
import urllib
import warnings

from diaspy import errors, streams


class Settings():
    """This object is used to get access to user's settings on
    Diaspora* and provides interface for downloading user's stuff.
    """
    def __init__(self, connection):
        self._connection = connection
    
    def downloadxml(self):
        """Returns downloaded XML.
        """
        request = self._connection.get('user/export')
        return request.text

    def downloadPhotos(self, size='large', path='.', _critical=False, _stream=None):
        """Downloads photos into the current working directory.
        Sizes are: large, medium, small.
        Filename is: {photo_guid}.{extension}

        Normally, this method will catch urllib-generated errors and
        just issue warnings about photos that couldn't be downloaded.
        However, with _critical param set to True errors will become
        critical - the will be reraised in finally block.

        :param size: size of the photos to download - large, medium or small
        :type size: str
        :param path: path to download (defaults to current working directory
        :type path: str
        :param _stream: diaspy.streams.Generic-like object (only for testing)
        :param _critical: if True urllib errors will be reraised after generating a warning (may be removed)

        :returns: integer, number of photos downloaded
        """
        photos = 0
        if _stream is not None: stream = _stream
        else: stream = streams.Activity
        stream = stream(self._connection)
        stream.full()
        for i, post in enumerate(stream):
            if post['photos']:
                for n, photo in enumerate(post['photos']):
                    name = '{0}.{1}'.format(photo['guid'], photo['sizes'][size].split('.')[-1])
                    filename = os.path.join(path, name)
                    try:
                        urllib.request.urlretrieve(url=photo['sizes'][size], filename=filename)
                    except (urllib.error.HTTPError, urllib.error.URLError) as e:
                        warnings.warn('downloading image {0} from post {1}: {2}'.format(photo['guid'], post['guid'], e))
                    finally:
                        if _critical: raise
                photos += 1
        return photos

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

        :param lang: language identifier from getLanguages()
        """
        data = {'_method': 'put', 'utf-8': '✓', 'user[language]': lang, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user', data=data)

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
