import requests
import re
import json


class Client:
    """This is the client class to connect to diaspora.

    .. note::

       Before calling any other function
       you have to call :func:`diaspy.Client.login`.

    """

    def __init__(self, pod):
        self._token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
        self.pod = pod
        self.session = requests.Session()

    def get_token(self):
        r = self.session.get(self.pod + "/stream")
        token = self._token_regex.search(r.text).group(1)
        return token


    def login(self, username, password):
        """This function is used to connect to the pod and log in.

        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str

        """
        self._username = username
        self._password = password
        r = self.session.get(self.pod + "/users/sign_in")
        token = self._token_regex.search(r.text).group(1)

        data = {'user[username]': self._username,
                'user[password]': self._password,
                'authenticity_token': token,
                'commit': ''}

        r = self.session.post(self.pod + "/users/sign_in", data=data)

    def post(self, text, aspect_id='public'):
        """This function sends a post to an aspect

        :param text: Text to post.
        :type text: str
        :param aspect_id: Aspect id to send post to.
        :type aspect_id: str

        """
        data = {'aspect_ids': aspect_id,
                'status_message[text]': text,
                'authenticity_token': self.get_token()}
        r = self.session.post(self.pod + "/status_messages", data=data)

    def get_user_info(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.

        """
        r = self.session.get(self.pod + "/stream")
        regex = re.compile(r'window.current_user_attributes = ({.*})')
        userdata = json.loads(regex.search(r.text).group(1))
        return userdata
