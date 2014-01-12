# -*- coding: utf-8 -*-

"""This module provides access to user's settings on Diaspora*.
"""


import json
import os
import re
import urllib
import warnings

from diaspy import errors, streams


class Account():
    """Provides interface to account settings.
    """
    email_regexp = re.compile('<input id="user_email" name="user\[email\]" size="30" type="text" value="(.+?)"')
    language_option_regexp = re.compile('<option value="([_a-zA-Z-]+)"(?: selected="selected")?>(.*?)</option>')

    def __init__(self, connection):
        self._connection = connection

    def downloadxml(self):
        """Returns downloaded XML.
        """
        request = self._connection.get('user/export')
        return request.text

    def downloadPhotos(self, size='large', path='.', mark_nsfw=True, _critical=False, _stream=None):
        """Downloads photos into the current working directory.
        Sizes are: large, medium, small.
        Filename is: {post_guid}_{photo_guid}.{extension}

        Normally, this method will catch urllib-generated errors and
        just issue warnings about photos that couldn't be downloaded.
        However, with _critical param set to True errors will become
        critical - the will be reraised in finally block.

        :param size: size of the photos to download - large, medium or small
        :type size: str
        :param path: path to download (defaults to current working directory
        :type path: str
        :param mark_nsfw: will append '-nsfw' to images from posts marked as nsfw,
        :type mark_nsfw: bool
        :param _stream: diaspy.streams.Generic-like object (only for testing)
        :param _critical: if True urllib errors will be reraised after generating a warning (may be removed)

        :returns: integer, number of photos downloaded
        """
        photos = 0
        if _stream is None:
            stream = streams.Activity(self._connection)
            stream.full()
        else:
            stream = _stream
        for i, post in enumerate(stream):
            if post['nsfw'] is not False: nsfw = '-nsfw'
            else: nsfw = ''
            if post['photos']:
                for n, photo in enumerate(post['photos']):
                    # photo format -- .jpg, .png etc.
                    ext = photo['sizes'][size].split('.')[-1]
                    name = '{0}_{1}{2}.{3}'.format(post['guid'], photo['guid'], nsfw, ext)
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
        data = {'_method': 'put', 'utf8': '✓', 'user[email]': email, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user', data=data, allow_redirects=False)
        if request.status_code != 302:
            raise errors.SettingsError('setting email failed: {0}'.format(request.status_code))

    def getEmail(self):
        """Returns currently used email.
        """
        data = self._connection.get('user/edit')
        email = self.email_regexp.search(data.text)
        if email is None: email = ''
        else: email = email.group(1)
        return email

    def setLanguage(self, lang):
        """Changes user's email.

        :param lang: language identifier from getLanguages()
        """
        data = {'_method': 'put', 'utf8': '✓', 'user[language]': lang, 'authenticity_token': repr(self._connection)}
        request = self._connection.post('user', data=data, allow_redirects=False)
        if request.status_code != 302:
            raise errors.SettingsError('setting language failed: {0}'.format(request.status_code))

    def getLanguages(self):
        """Returns a list of tuples containing ('Language name', 'identifier').
        One of the Black Magic(tm) methods.
        """
        request = self._connection.get('user/edit')
        return self.language_option_regexp.findall(request.text)


class Privacy():
    """Provides interface to provacy settings.
    """
    def __init__(self, connection):
        self._connection = connection


class Profile():
    """Provides interface to profile settigns.

    WARNING:

        Because of the way update requests for profile are created every field must be sent.
        The `load()` method is used to load all information into the dictionary.
        Setters can then be used to adjust the data.
        Finally, `update()` can be called to send data back to pod.
    """
    firstname_regexp = re.compile('id="profile_first_name" name="profile\[first_name\]" type="text" value="(.*?)" />')
    lastname_regexp = re.compile('id="profile_last_name" name="profile\[last_name\]" type="text" value="(.*?)" />')
    bio_regexp = re.compile('<textarea id="profile_bio" name="profile\[bio\]" placeholder="Fill me out" rows="5">\n(.*?)</textarea>')
    location_regexp = re.compile('id="profile_location" name="profile\[location\]" placeholder="Fill me out" type="text" value="(.*?)" />')
    gender_regexp = re.compile('id="profile_gender" name="profile\[gender\]" placeholder="Fill me out" type="text" value="(.*?)" />')
    birth_year_regexp = re.compile('selected="selected" value="([0-9]{4,4})">[0-9]{4,4}</option>')
    birth_month_regexp = re.compile('selected="selected" value="([0-9]{1,2})">(.*?)</option>')
    birth_day_regexp = re.compile('selected="selected" value="([0-9]{1,2})">[0-9]{1,2}</option>')
    is_searchable_regexp = re.compile('checked="checked" id="profile_searchable" name="profile\[searchable\]" type="checkbox" value="(.*?)" />')
    is_nsfw_regexp = re.compile('checked="checked" id="profile_nsfw" name="profile\[nsfw\]" type="checkbox" value="(.*?)" />')

    def __init__(self, connection, no_load=False):
        self._connection = connection
        self.data = {'utf-8': '✓',
                     '_method': 'put',
                     'profile[first_name]': '',
                     'profile[last_name]': '',
                     'profile[tag_string]': '',
                     'tags': '',
                     'file': '',
                     'profile[bio]': '',
                     'profile[location]': '',
                     'profile[gender]': '',
                     'profile[date][year]': '',
                     'profile[date][month]': '',
                     'profile[date][day]': '',
                     }
        self._html = self._fetchhtml()
        self._loaded = False
        if not no_load: self.load()

    def _fetchhtml(self):
        """Fetches html that will be used to extract data.
        """
        return self._connection.get('profile/edit').text

    def getName(self):
        """Returns two-tuple: (first, last) name.
        """
        first = self.firstname_regexp.search(self._html).group(1)
        last = self.lastname_regexp.search(self._html).group(1)
        return (first, last)

    def getTags(self):
        """Returns tags user had selected when describing him/her-self.
        """
        guid = self._connection.getUserData()['guid']
        html = self._connection.get('people/{0}'.format(guid)).text
        description_regexp = re.compile('<a href="/tags/(.*?)" class="tag">#.*?</a>')
        return [tag.lower() for tag in re.findall(description_regexp, html)]

    def getBio(self):
        """Returns user bio.
        """
        bio = self.bio_regexp.search(self._html).group(1)
        return bio

    def getLocation(self):
        """Returns location string.
        """
        location = self.location_regexp.search(self._html).group(1)
        return location

    def getGender(self):
        """Returns location string.
        """
        gender = self.gender_regexp.search(self._html).group(1)
        return gender

    def getBirthDate(self, named_month=False):
        """Returns three-tuple: (year, month, day).

        :param named_month: if True, return name of the month instead of integer
        :type named_month: bool
        """
        year = self.birth_year_regexp.search(self._html)
        if year is None: year = -1
        else: year = int(year.group(1))
        month = self.birth_month_regexp.search(self._html)
        if month is None:
            if named_month: month = ''
            else: month = -1
        else:
            if named_month:
                month = month.group(2)
            else:
                month = int(month.group(1))
        day = self.birth_day_regexp.search(self._html)
        if day is None: day = -1
        else: day = int(day.group(1))
        return (year, month, day)

    def isSearchable(self):
        """Returns True if profile is searchable.
        """
        searchable = self.is_searchable_regexp.search(self._html)
        # this is because value="true" in every case so we just
        # check if the field is "checked"
        if searchable is None: searchable = False  # if it isn't - the regexp just won't match
        else: searchable = True
        return searchable

    def isNSFW(self):
        """Returns True if profile is marked as NSFW.
        """
        nsfw = self.is_nsfw_regexp.search(self._html)
        if nsfw is None: nsfw = False
        else: nsfw = True
        return nsfw

    def setName(self, first, last):
        """Set first and last name.
        """
        self.data['profile[first_name]'] = first
        self.data['profile[last_name]'] = last

    def setTags(self, tags):
        """Sets tags that describe the user.
        """
        self.data['tags'] = ', '.join(['#{}'.format(tag) for tag in tags])

    def setBio(self, bio):
        """Set bio of a user.
        """
        self.data['profile[bio]'] = bio

    def setLocation(self, location):
        """Set location of a user.
        """
        self.data['profile[location]'] = location

    def setGender(self, gender):
        """Set gender of a user.
        """
        self.data['profile[gender]'] = gender

    def setBirthDate(self, year, month, day):
        """Set birth date of a user.
        """
        self.data['profile[date][year]'] = year
        self.data['profile[date][month]'] = month
        self.data['profile[date][day]'] = day

    def setSearchable(self, searchable):
        """Set user's searchable status.
        """
        self.data['profile[searchable]'] = json.dumps(searchable)

    def setNSFW(self, nsfw):
        """Set user NSFW status.
        """
        self.data['profile[nsfw]'] = json.dumps(nsfw)

    def load(self):
        """Loads profile data into self.data dictionary.
        **Notice:** Not all keys are loaded yet.
        """
        self.setName(*self.getName())
        self.setBio(self.getBio())
        self.setLocation(self.getLocation())
        self.setGender(self.getGender())
        self.setBirthDate(*self.getBirthDate(named_month=False))
        self.setSearchable(self.isSearchable())
        self.setNSFW(self.isNSFW())
        self.setTags(self.getTags())
        self._loaded = True

    def update(self):
        """Updates profile information.
        """
        if not self._loaded: raise errors.DiaspyError('profile was not loaded')
        self.data['authenticity_token'] = repr(self._connection)
        print(self.data)
        request = self._connection.post('profile', data=self.data, allow_redirects=False)
        return request.status_code


class Services():
    """Provides interface to services settings.
    """
    def __init__(self, connection):
        self._connection = connection
