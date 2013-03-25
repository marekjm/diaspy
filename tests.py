#!/usr/bin/env python3

import unittest
import getpass

#   failure to import any of the modules below indicates failed tests
#   modules used by diaspy
import requests, re
#   actual diaspy code
import diaspy


####    test suite configuration variables: can be adjusted to your liking
#   pod used by tests (has to be valid)
__pod__ = 'http://pod.orkz.net'
__username__ = 'testuser'
__passwd__ = 'testpassword'


class ClientTests(unittest.TestCase):
    def testInitialization(self):
        """This test checks initialization of Client() instance.
        """
        client = diaspy.client.Client(pod=__pod__, username=__username__, password=__passwd__)
        self.assertEqual(__pod__, client.pod)
        self.assertEqual(__username__, client._username)
        self.assertEqual(__passwd__, client._password)
        self.assertEqual(None, client._post_data)
        self.assertEqual(client._token_regex, re.compile(r'content="(.*?)"\s+name="csrf-token'))
        self.assertEqual(client._login_data['user[username]'], 'testuser')
        self.assertEqual(client._login_data['user[password]'], 'testpassword')
        self.assertEqual(client._login_data['authenticity_token'], client.get_token())

    def testPreparationOfPostData(self):
        """This test checks correctness of data set for posting.
        """


    
if __name__ == '__main__': 
    __passwd__ = getpass.getpass(prompt='Password used for testing: ')
    if __passwd__ == '': __passwd__ = 'testpassword'
    unittest.main()
