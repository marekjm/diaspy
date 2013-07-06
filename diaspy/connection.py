#!/usr/bin/env python

import re
import requests
import json
import warnings


"""This module abstracts connection to pod.
"""


class LoginError(Exception):
    pass


class TokenError(Exception):
    pass


class Connection():
    """Object representing connection with the server.
    It is pushed around internally and is considered private.
    """
    _token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
    _userinfo_regex = re.compile(r'window.current_user_attributes = ({.*})')
    login_data = {}
    token = ''

    def __init__(self, pod, username='', password=''):
        """
        :param pod: The complete url of the diaspora pod to use.
        :type pod: str
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str
        """
        self.pod = pod
        self.session = requests.Session()
        try:
            self._setlogin(username, password)
        except Exception as e:
            raise LoginError('cannot create login data (caused by: {0}'.format(e))

    def get(self, string, headers={}, params={}):
        """This method gets data from session.
        Performs additional checks if needed.

        Example:
            To obtain 'foo' from pod one should call `get('foo')`.

        :param string: URL to get without the pod's URL and slash eg. 'stream'.
        :type string: str
        """
        return self.session.get('{0}/{1}'.format(self.pod, string), params=params, headers=headers)

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
        request = self.session.post(string, data, headers=headers, params=params)
        return request

    def put(self, string, data=None, headers={}, params={}):
        """This method PUTs to session.
        """
        string = '{0}/{1}'.format(self.pod, string)
        if data is not None: request = self.session.put(string, data, headers=headers, params=params)
        else: request = self.session.put(string, headers=headers, params=params)
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
        request = self.session.delete(string, data=data, headers=headers)
        return request

    def _setlogin(self, username, password):
        """This function is used to set data for login.

        .. note::
            It should be called before _login() function.
        """
        self.username, self.password = username, password
        self.login_data = {'user[username]': self.username,
                           'user[password]': self.password,
                           'authenticity_token': self._fetchtoken()}

    def _login(self):
        """Handles actual login request.
        Raises LoginError if login failed.
        """
        request = self.post('users/sign_in',
                            data=self.login_data,
                            headers={'accept': 'application/json'})
        if request.status_code != 201:
            raise LoginError('{0}: login failed'.format(request.status_code))

    def login(self, username='', password=''):
        """This function is used to log in to a pod.
        Will raise LoginError if password or username was not specified.
        """
        if username and password: self._setlogin(username, password)
        if not self.username or not self.password: raise LoginError('password or username not specified')
        self._login()

    def logout(self):
        """Logs out from a pod.
        When logged out you can't do anything.
        """
        self.get('users/sign_out')
        self.username = ''
        self.token = ''
        self.password = ''

    def podswitch(self, pod):
        """Switches pod from current to another one.
        """
        self.pod = pod
        self._login()

    def getUserInfo(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.
        """
        request = self.get('bookmarklet')
        userdata = json.loads(self._userinfo_regex.search(request.text).group(1))
        return userdata

    def _fetchtoken(self):
        """This method tries to get token string needed for authentication on D*.

        :returns: token string
        """
        request = self.get('stream')
        token = self._token_regex.search(request.text).group(1)
        return token

    def get_token(self, new=False):
        """This function returns a token needed for authentication in most cases.
        Each time it is run a _fetchtoken() is called and refreshed token is stored.

        It is more safe to use than _fetchtoken().
        By setting new you can request new token or decide to get stored one.
        If no token is stored new one will be fatched anyway.

        :returns: string -- token used to authenticate
        """
        try:
            if new: self.token = self._fetchtoken()
            if not self.token: self.token = self._fetchtoken()
        except requests.exceptions.ConnectionError as e:
            warnings.warn('{0} was cought: reusing old token'.format(e))
        finally:
            if not self.token: raise TokenError('cannot obtain token and no previous token found for reuse')
        return self.token
        
    def lookup_user(self, handle):
        """This function will launch a webfinger lookup from the pod for the
        handle requested. Nothing is returned but if the lookup was successful,
        user should soon be searchable via this pod.
        
        :param string: Handle to search for.
        """
        request = self.get('people', headers={'accept': 'text/html'}, params={'q':handle})
