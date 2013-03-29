#!/usr/bin/env python3

import unittest
import getpass

#   failure to import any of the modules below indicates failed tests
#   modules used by diaspy
import requests, re
#   actual diaspy code
import diaspy


####    test suite configuration variables: can be adjusted to your liking
import testconf
__pod__ = testconf.__pod__
__username__ = testconf.__username__
__passwd__ = testconf.__passwd__


class ClientTests(unittest.TestCase):
    def testInitialization(self):
        client = diaspy.client.Client(pod=__pod__, username=__username__, password=__passwd__)
        self.assertEqual(__pod__, client.pod)
        self.assertEqual(__username__, client._username)
        self.assertEqual(__passwd__, client._password)
        self.assertEqual({}, client._post_data)
        self.assertEqual(client._token_regex, re.compile(r'content="(.*?)"\s+name="csrf-token'))
        self.assertEqual(client._login_data['user[username]'], __username__)
        self.assertEqual(client._login_data['user[password]'], __passwd__)
        self.assertEqual(client._login_data['authenticity_token'], client.get_token())

    def testGettingTag(self):
        client = diaspy.client.Client(pod=__pod__, username=__username__, password=__passwd__)
        tag = client.get_tag('foo')
        self.assertEqual(list, type(tag))
        if tag: self.assertEqual(diaspy.models.Post, type(tag[0]))

    def testGettingMailbox(self):
        client = diaspy.client.Client(pod=__pod__, username=__username__, password=__passwd__)
        mailbox = client.get_mailbox()
        self.assertEqual(list, type(mailbox))
        self.assertEqual(diaspy.conversations.Conversation, type(mailbox[0]))

if __name__ == '__main__': unittest.main()
