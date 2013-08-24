#!/usr/bin/env python

import re
import requests
import json
import warnings

from diaspy import errors


"""This module abstracts connection to pod.
"""


class Connection():
    """Object representing connection with the pod.
    """
    _token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
    _userinfo_regex = re.compile(r'window.current_user_attributes = ({.*})')

    def __init__(self, pod, username='', password='', schema='https'):
        """
        :param pod: The complete url of the diaspora pod to use.
        :type pod: str
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str
        """
        self.pod = pod
        self._session = requests.Session()
        self._login_data = {}
        self._token = ''
        try:
            self._setlogin(username, password)
        except requests.exceptions.MissingSchema:
            self.pod = '{0}://{1}'.format(schema, self.pod)
            warnings.warn('schema was missing')
        finally:
            pass
        try:
            self._setlogin(username, password)
        except Exception as e:
            raise errors.LoginError('cannot create login data (caused by: {0})'.format(e))

    def __repr__(self):
        """Returns token string.
        It will be easier to change backend if programs will just use:
            repr(connection)
        instead of calling a specified method.
        """
        return self._token

    def get(self, string, headers={}, params={}):
        """This method gets data from session.
        Performs additional checks if needed.

        Example:
            To obtain 'foo' from pod one should call `get('foo')`.

        :param string: URL to get without the pod's URL and slash eg. 'stream'.
        :type string: str
        """
        return self._session.get('{0}/{1}'.format(self.pod, string), params=params, headers=headers)

    def post(self, string, data, headers={}, params={}):
        """This method posts data to session.
        Performs additional checks if needed.

        Example:
            To post to 'foo' one should call `post('foo', data={})`.

        :param string: URL to post without the pod's URL and slash eg. 'status_messages'.
        :type string: str
        :param data: Data to post.
        :param headers: Headers (optional).
        :type headers: dict
        :param params: Parameters (optional).
        :type params: dict
        """
        string = '{0}/{1}'.format(self.pod, string)
        request = self._session.post(string, data, headers=headers, params=params)
        return request

    def put(self, string, data=None, headers={}, params={}):
        """This method PUTs to session.
        """
        string = '{0}/{1}'.format(self.pod, string)
        if data is not None: request = self._session.put(string, data, headers=headers, params=params)
        else: request = self._session.put(string, headers=headers, params=params)
        return request

    def delete(self, string, data, headers={}):
        """This method lets you send delete request to session.
        Performs additional checks if needed.

        :param string: URL to use.
        :type string: str
        :param data: Data to use.
        :param headers: Headers to use (optional).
        :type headers: dict
        """
        string = '{0}/{1}'.format(self.pod, string)
        request = self._session.delete(string, data=data, headers=headers)
        return request

    def _setlogin(self, username, password):
        """This function is used to set data for login.

        .. note::
            It should be called before _login() function.
        """
        self._login_data = {'user[username]': username,
                            'user[password]': password,
                            'authenticity_token': self._fetchtoken()}

    def _login(self):
        """Handles actual login request.
        Raises LoginError if login failed.
        """
        request = self.post('users/sign_in',
                            data=self._login_data,
                            headers={'accept': 'application/json'})
        if request.status_code != 201:
            raise errors.LoginError('{0}: login failed'.format(request.status_code))

    def login(self, username='', password=''):
        """This function is used to log in to a pod.
        Will raise LoginError if password or username was not specified.
        """
        if username and password: self._setlogin(username, password)
        if not self._login_data['user[username]'] or not self._login_data['user[password]']:
            raise errors.LoginError('username and/or password is not specified')
        self._login()
        self._login_data = {}

    def logout(self):
        """Logs out from a pod.
        When logged out you can't do anything.
        """
        self.get('users/sign_out')
        self.token = ''

    def podswitch(self, pod, username, password):
        """Switches pod from current to another one.
        """
        self.pod = pod
        self._setlogin(username, password)
        self._login()

    def getUserInfo(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.
        """
        request = self.get('bookmarklet')
        try:
            userdata = json.loads(self._userinfo_regex.search(request.text).group(1))
        except AttributeError:
            raise errors.DiaspyError('cannot find user data')
        return userdata

    def _fetchtoken(self):
        """This method tries to get token string needed for authentication on D*.

        :returns: token string
        """
        request = self.get('stream')
        token = self._token_regex.search(request.text).group(1)
        self._token = token
        return token

    def get_token(self, fetch=False):
        """This function returns a token needed for authentication in most cases.
        **Notice:** using repr() is recommended method for getting token.

        :returns: string -- token used to authenticate
        """
        try:
            if fetch: self._fetchtoken()
            if not self._token: self._fetchtoken()
        except requests.exceptions.ConnectionError as e:
            warnings.warn('{0} was cought: reusing old token'.format(e))
        finally:
            if not self._token: raise errors.TokenError('cannot obtain token and no previous token found for reuse')
        return self._token
