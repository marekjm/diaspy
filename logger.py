#!/usr/bin/env python3

"""Module used for obtaining (pod, username, password) tuple.

Used by me when I want to debug in public places and not want to show
my password.
"""

import getpass


def getdata():
    """Asks for data.
    """
    pod = input('Pod: ')
    username = input('Username at \'{0}\': '.format(pod))
    password = getpass.getpass('Password for {0}@{1}: '.format(username, pod))
    return (pod, username, password)
