#!/usr/bin/env python

import re
import requests
import json


class LoginError(Exception):
    pass


class Connection():
    """Object representing connection with the server.
    It is pushed around internally and is considered private.
    """
    _token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
    _userinfo_regex = re.compile(r'window.current_user_attributes = ({.*})')
    login_data = {}

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
        self._setlogin(username, password)

    def get(self, string):
        """This method gets data from session.
        Performs additional checks if needed.

        Example:
            To obtain 'foo' from pod one should call `get('foo')`.

        :param string: URL to get without the pod's URL and slash eg. 'stream'.
        :type string: str
        """
        return self.session.get('{0}/{1}'.format(self.pod, string))

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
                           'authenticity_token': self.get_token()}

    def _login(self):
        """Handles actual login request.
        Raises LoginError if login failed.
        """
        request = self.post('users/sign_in',
                            data=self.login_data,
                            headers={'accept': 'application/json'})
        if request.status_code != 201:
            raise LoginError('{0}: Login failed.'.format(request.status_code))

    def login(self, username='', password=''):
        """This function is used to log in to a pod.
        Will raise LoginError if password or username was not specified.
        """
        if username and password: self._setlogin(username, password)
        if not self.username or not self.password: raise LoginError('password or username not specified')
        self._login()

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

    def get_token(self):
        """This function returns a token needed for authentication in most cases.

        :returns: string -- token used to authenticate
        """
        r = self.get('stream')
        token = self._token_regex.search(r.text).group(1)
        return token
