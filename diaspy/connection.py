#!/usr/bin/env python


class Connection():
    """Object representing connection with the server.
    It is pushed around internally and is considered private.
    """
    def __init__(self, pod, username='', password=''):
        self.pod = pod
        self.username, self.password = username, password

