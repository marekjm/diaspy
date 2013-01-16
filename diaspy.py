"""
.. module:: diaspy
   :platform: Unix, Windows
   :synopsis: Simple python api for diaspora

.. moduleauthor:: Moritz Kiefer <moritz.kiefer@gmail.com>


"""
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
        self._pod = pod
        self._session = requests.Session()

    def _get_token(self):
        r = self._session.get(self._pod + "/stream")
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
        r = self._session.get(self._pod + "/users/sign_in")
        token = self._token_regex.search(r.text).group(1)

        data = {'user[username]': self._username,
                'user[password]': self._password,
                'authenticity_token': token,
                'commit': ''}

        r = self._session.post(self._pod + "/users/sign_in", data=data)

    def post(self, text, aspect_id='public'):
        """This function sends a post to an aspect

        :param text: Text to post.
        :type text: str
        :param aspect_id: Aspect id to send post to.
        :type aspect_id: str

        """
        data = {'aspect_ids': aspect_id,
                'status_message[text]': text,
                'authenticity_token': self._get_token()}
        r = self._session.post(self._pod + "/status_messages", data=data)

    def get_user_info(self):
        """This function returns the current user's attributes.

        :returns: dict -- json formatted user info.

        """
        r = self._session.get(self._pod + "/stream")
        regex = re.compile(r'window.current_user_attributes = ({.*})')
        userdata = json.loads(regex.search(r.text).group(1))
        return userdata

    def like(self, post_id):
        """This function likes a post

        :param post_id: id of the post to like.
        :type post_id: str
        :returns: dict -- json formatted like object.

        """

        data = {'authenticity_token': self._get_token()}

        r = self._session.post(self._pod + "/posts/" +
                post_id + "/likes", data=data, headers={'accept': 'application/json'})
        return r.json()

    def rmlike(self, post_id, like_id):
        """This function removes a like from a post

        :param post_id: id of the post to remove the like from.
        :type post_id: str
        :param like_id: id of the like to remove.
        :type like_id: str

        """

        data = {'authenticity_token': self._get_token()}

        r = self._session.delete(self._pod + "/posts/" + 
                                 post_id + "/likes/" +
                                 like_id,
                                 data=data)

    def reshare(self, post_guid):
        """This function reshares a post

        :param post_id: id of the post to resahre.
        :type post_id: str

        """

        data = {'root_guid': post_guid,
                'authenticity_token': self._get_token()}

        r = self._session.post(self._pod + "/reshares", data=data)
        print(r.text)
