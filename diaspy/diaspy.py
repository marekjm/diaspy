"""
.. module:: diaspora_api.diaspy
   :platform: Unix, Windows
   :synopsis: Simple python api for diaspora

.. moduleauthor:: Moritz Kiefer <moritz.kiefer@gmail.com>


"""
import requests
import re

class Client:
    """This is the client class to connect to diaspora.

    .. note::

       Before calling any other function you have to call :func:`diaspy.diaspy.Client.login`.

    """

    def __init__(self, pod):
        self._token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
        self._pod = pod
        self._session = requests.Session()

    def login(self, username, password):
        """blablablalbla"""
        self._username = username
        self._password = password
        r = self._session.get(self._pod + "/users/sign_in")
        token = self._token_regex.search(r.text).group(1)

        data = {'user[username]': self._username,
                'user[password]': self._password,
                'authenticity_token': token,
                'commit':''}

        r = self._session.post(self._pod + "/users/sign_in", data=data)

    def post(self, text, aspect_id='public'):
        """blablablalbla"""
        r = self._session.get(self._pod + "/stream")
        token = self._token_regex.search(r.text).group(1)
        data = {'aspect_ids': aspect_id,
                'status_message[text]': text,
                'authenticity_token': token}
        r = self._session.post(self._pod + "/status_messages", data=data)
