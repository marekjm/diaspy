import requests
import re
import json


class Client:
    """This is the client class to connect to diaspora.

    """

    def __init__(self, pod, username, password):
        """
        :param pod: The complete url of the diaspora pod to use.
        :type pod: str
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str

        """
        self._token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
        self.pod = pod
        self.session = requests.Session()
        self._login(username, password)

    def get_token(self):
        """This function gets a token needed for authentication in most cases

        :returns: string -- token used to authenticate

        """

        r = self.session.get(self.pod + '/stream')
        token = self._token_regex.search(r.text).group(1)
        return token

    def _login(self, username, password):
        """This function is used to connect to the pod and log in.
        .. note::
           This function shouldn't be called manually.
        """
        self._username = username
        self._password = password
        r = self.session.get(self.pod + '/users/sign_in')
        token = self._token_regex.search(r.text).group(1)

        data = {'user[username]': self._username,
                'user[password]': self._password,
                'authenticity_token': token,
                'commit': ''}

        r = self.session.post(self.pod +
                              '/users/sign_in',
                              data=data,
                              headers={'accept': 'application/json'})

        if r.status_code != 201:
            raise Exception(str(r.status_code) + ': Login failed.')

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
        r = self.session.post(self.pod +
                              "/status_messages",
                              data=data,
                              headers={'accept': 'application/json'})
        if r.status_code != 201:
            raise Exception(str(r.status_code) + ': Post could not be posted.')

        return r.json()

    def get_user_info(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.

        """
        r = self.session.get(self.pod + '/stream')
        regex = re.compile(r'window.current_user_attributes = ({.*})')
        userdata = json.loads(regex.search(r.text).group(1))
        return userdata
