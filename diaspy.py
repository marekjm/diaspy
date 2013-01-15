"""
.. module:: diaspy
   :platform: Unix, Windows
   :synopsis: Simple python api for diaspora

.. moduleauthor:: Moritz Kiefer <moritz.kiefer@gmail.com>


"""
import requests
import re

class Client:
    """This is the client class to connect to diaspora.

    .. note::

       Before calling any other function you have to call :func:`diaspy.Client.login`.

    """

    def __init__(self, pod):
        self._token_regex = re.compile(r'content="(.*?)"\s+name="csrf-token')
        self._pod = pod
        self._session = requests.Session()

    def login(self, username, password):
        """This function is used to connect to the pod and log in.
        
        :param username: The username used to log in.
        :type username: str
        :param password: The password used to log in.
        :type password: str
        
        """
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
        """This function sends a post to an aspect
        
        :param text: Text to post.
        :type text: str
        :param aspect_id: Aspect id to send post to.
        :type aspect_id: str
        
        """
        r = self._session.get(self._pod + "/stream")
        token = self._token_regex.search(r.text).group(1)
        data = {'aspect_ids': aspect_id,
                'status_message[text]': text,
                'authenticity_token': token}
        r = self._session.post(self._pod + "/status_messages", data=data)
