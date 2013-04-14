#!/usr/bin/env python3

import unittest

#   failure to import any of the modules below indicates failed tests
#   modules used by diaspy
import requests
import re
#   actual diaspy code
import diaspy


####    test suite configuration variables: can be adjusted to your liking
import testconf
__pod__ = testconf.__pod__
__username__ = testconf.__username__
__passwd__ = testconf.__passwd__


class ConnectionTest(unittest.TestCase):
    def testLoginWithoutUsername(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, password='foo')

    def testLoginWithoutPassword(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, username='user')

class ClientTests(unittest.TestCase):
    def testGettingUserInfo(self):
        client = diaspy.client.Client(__pod__, __username__, __passwd__)
        info = client.get_user_info()
        self.assertEqual(dict, type(info))

    def testGettingStream(self):
        client = diaspy.client.Client(__pod__, __username__, __passwd__)
        stream = client.get_stream()
        self.assertEqual(list, type(stream))
        if stream: self.assertEqual(diaspy.models.Post, type(stream[0]))

    def testGettingNotifications(self):
        client = diaspy.client.Client(__pod__, __username__, __passwd__)
        notifications = client.get_notifications()
        self.assertEqual(list, type(notifications))
        if notifications: self.assertEqual(dict, type(notifications[0]))

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
