#!/usr/bin/env python

import re
import requests


class LoginError(Exception):
    pass


class Connection():
    """Object representing connection with the server.
    It is pushed around internally and is considered private.
    """
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
        self._token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
        self._setlogin(username, password)

    def get(self, string):
        """This method gets data from session.
        Performs additional checks if needed.

        Example:
            To obtain 'foo' from pod one should call `_sessionget('foo')`.

        :param string: URL to get without the pod's URL and slash eg. 'stream'.
        :type string: str
        """
        return self.session.get('{0}/{1}'.format(self.pod, string))

    def post(self, string, data, headers={}, params={}):
        """This method posts data to session.
        Performs additional checks if needed.

        Example:
            To post to 'foo' one should call `_sessionpost('foo', data={})`.

        :param string: URL to post without the pod's URL and slash eg. 'status_messages'.
        :type string: str
        :param data: Data to post.
        :param headers: Headers (optional).
        :type headers: dict
        :param params: Parameters (optional).
        :type params: dict
        """
        string = '{0}/{1}'.format(self.pod, string)
        if headers and params:
            request = self.session.post(string, data=data, headers=headers, params=params)
        elif headers and not params:
            request = self.session.post(string, data=data, headers=headers)
        elif not headers and params:
            request = self.session.post(string, data=data, params=params)
        else:
            request = self.session.post(string, data=data)
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
        if headers:
            request = self.session.delete(string, data=data, headers=headers)
        else:
            request = self.session.delete(string, data=data)
        return request

    def _setlogin(self, username, password):
        """This function is used to set data for login.
        .. note::
            It should be called before _login() function.
        """
        self.username, self.password = username, password
        self.login_data = {'user[username]': self.username,
                           'user[password]': self.password,
                           'authenticity_token': self.getToken()}

    def _login(self):
        """Handles actual login request.
        Raises LoginError if login failed.
        """
        request = self.post('users/sign_in',
                            data=self.login_data,
                            headers={'accept': 'application/json'})
        if request.status_code != 201:
            raise Exception('{0}: Login failed.'.format(request.status_code))

    def login(self, username='', password=''):
        """This function is used to log in to a pod.
        Will raise LoginError if password or username was not specified.
        """
        if username and password: self._setlogin(username, password)
        if not self.username or not self.password: raise LoginError('password or username not specified')
        self._login()

    def podswitch(self, pod):
        """Switches pod.
        """
        self.pod = pod
        self._login()

    def getToken(self):
        """This function returns a token needed for authentication in most cases.

        :returns: string -- token used to authenticate
        """
        r = self.get('stream')
        token = self._token_regex.search(r.text).group(1)
        return token
