#!/usr/bin/env python3

import unittest

#   failing to import any of the modules below indicates failed tests
#   modules used by diaspy
import requests, re
#   actual diaspy code
import diaspy


####    test suite configuration variables: can be adjusted to your liking
#   pod used by tests (has to be valid)
__pod__ = "http://pod.orkz.net"


class ClientTests(unittest.TestCase):
    def testInit(self):
        """
        This test checks initialization of Client() instance.
        """
        client = diaspy.client.Client(pod=__pod__, username='testuser', password='testpassword')
        self.assertEqual(__pod__, client.pod)
        self.assertEqual('testuser', client._username)
        self.assertEqual('testpassword', client._password)
        self.assertEqual(client._token_regex, re.compile(r'content="(.*?)"\s+name="csrf-token'))
        self.assertEqual(client._login_data['user[username]'], 'testuser')
        self.assertEqual(client._login_data['user[password]'], 'testpassword')
        self.assertEqual(client._login_data['authenticity_token'], client.get_token())

    
if __name__ == "__main__": unittest.main()
