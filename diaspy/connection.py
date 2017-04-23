#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This module abstracts connection to pod.
"""


import json
import re
import requests
import warnings

from diaspy import errors


DEBUG = True


class Connection():
    """Object representing connection with the pod.
    """
    _token_regex = re.compile(r'name="csrf-token"\s+content="(.*?)"')
    _userinfo_regex = re.compile(r'window.current_user_attributes = ({.*})')
    # this is for older version of D*
    _token_regex_2 = re.compile(r'content="(.*?)"\s+name="csrf-token')
    _userinfo_regex_2 = re.compile(r'gon.user=({.*});gon.preloads')
    _verify_SSL = True

    def __init__(self, pod, username, password, schema='https'):
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
        self._login_data = {'user[remember_me]': 1, 'utf8': '✓'}
        self._userdata = {}
        self._token = ''
        self._diaspora_session = ''
        self._cookies = self._fetchcookies()
        self._fetch_token_from = 'stream'
        try:
            #self._setlogin(username, password)
            self._login_data = {'user[username]': username,
                                'user[password]': password,
                                'authenticity_token': self._fetchtoken()}
            success = True
        except requests.exceptions.MissingSchema:
            self.pod = '{0}://{1}'.format(schema, self.pod)
            warnings.warn('schema was missing')
            success = False
        finally:
            pass
        try:
            if not success:
                self._login_data = {'user[username]': username,
                                    'user[password]': password,
                                    'authenticity_token': self._fetchtoken()}
        except Exception as e:
            raise errors.LoginError('cannot create login data (caused by: {0})'.format(e))

    def _fetchcookies(self):
        request = self.get('stream')
        return request.cookies

    def __repr__(self):
        """Returns token string.
        It will be easier to change backend if programs will just use:
            repr(connection)
        instead of calling a specified method.
        """
        return self._fetchtoken()

    def get(self, string, headers={}, params={}, direct=False, **kwargs):
        """This method gets data from session.
        Performs additional checks if needed.

        Example:
            To obtain 'foo' from pod one should call `get('foo')`.

        :param string: URL to get without the pod's URL and slash eg. 'stream'.
        :type string: str
        :param direct: if passed as True it will not be expanded
        :type direct: bool
        """
        if not direct: url = '{0}/{1}'.format(self.pod, string)
        else: url = string
        return self._session.get(url, params=params, headers=headers, verify=self._verify_SSL, **kwargs)

    def tokenFrom(self, location):
        """Sets location for the *next* fetch of CSRF token.
        Intended to be used for oneliners like this one:

            connection.tokenFrom('somewhere').delete(...)

        where the token comes from "somewhere" instead of the
        default stream page.
        """
        self._fetch_token_from = location
        return self

    def post(self, string, data, headers={}, params={}, **kwargs):
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
        if 'X-CSRF-Token' not in headers:
            headers['X-CSRF-Token'] = self.get_token()
        request = self._session.post(string, data, headers=headers, params=params, verify=self._verify_SSL, **kwargs)
        return request

    def put(self, string, data=None, headers={}, params={}, **kwargs):
        """This method PUTs to session.
        """
        string = '{0}/{1}'.format(self.pod, string)
        if 'X-CSRF-Token' not in headers:
            headers['X-CSRF-Token'] = self.get_token()
        if data is not None: request = self._session.put(string, data, headers=headers, params=params, **kwargs)
        else: request = self._session.put(string, headers=headers, params=params, verify=self._verify_SSL, **kwargs)
        return request

    def delete(self, string, data = None, headers={}, **kwargs):
        """This method lets you send delete request to session.
        Performs additional checks if needed.

        :param string: URL to use.
        :type string: str
        :param data: Data to use.
        :param headers: Headers to use (optional).
        :type headers: dict
        """
        string = '{0}/{1}'.format(self.pod, string)
        if 'X-CSRF-Token' not in headers:
            headers['X-CSRF-Token'] = self.get_token()
        request = self._session.delete(string, data=data, headers=headers, verify=self._verify_SSL, **kwargs)
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
                            allow_redirects=False)
        if request.status_code != 302:
            raise errors.LoginError('{0}: login failed'.format(request.status_code))

    def login(self, remember_me=1):
        """This function is used to log in to a pod.
        Will raise LoginError if password or username was not specified.
        """
        if not self._login_data['user[username]'] or not self._login_data['user[password]']:
            raise errors.LoginError('username and/or password is not specified')
        self._login_data['user[remember_me]'] = remember_me
        status = self._login()
        self._login_data = {}
        return self

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

    def _fetchtoken(self):
        """This method tries to get token string needed for authentication on D*.

        :returns: token string
        """
        request = self.get(self._fetch_token_from)
        token = self._token_regex.search(request.text)
        if token is None: token = self._token_regex_2.search(request.text)
        if token is not None: token = token.group(1)
        else: raise errors.TokenError('could not find valid CSRF token')
        self._token = token
        self._fetch_token_from = 'stream'
        return token

    def get_token(self, fetch=True):
        """This function returns a token needed for authentication in most cases.
        **Notice:** using repr() is recommended method for getting token.

        Each time it is run a _fetchtoken() is called and refreshed token is stored.

        It is more safe to use than _fetchtoken().
        By setting new you can request new token or decide to get stored one.
        If no token is stored new one will be fetched anyway.

        :returns: string -- token used to authenticate
        """
        try:
            if fetch or not self._token: self._fetchtoken()
        except requests.exceptions.ConnectionError as e:
            warnings.warn('{0} was cought: reusing old token'.format(e))
        finally:
            if not self._token: raise errors.TokenError('cannot obtain token and no previous token found for reuse')
        return self._token

    def getSessionToken(self):
        """Returns session token string (_diaspora_session).
        """
        return self._diaspora_session

    def getUserData(self):
        """Returns user data.
        """
        request = self.get('bookmarklet')
        userdata = self._userinfo_regex.search(request.text)
        if userdata is None: userdata = self._userinfo_regex_2.search(request.text)
        if userdata is None: raise errors.DiaspyError('cannot find user data')
        userdata = userdata.group(1)
        return json.loads(userdata)

    def set_verify_SSL(self, verify):
        """Sets whether there should be an error if a SSL-Certificate could not be verified.
        """
        self._verify_SSL = verify
