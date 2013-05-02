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

__connection__ = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
__connection__.login()


class StreamTest(unittest.TestCase):
    def testGetting(self):
        c = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
        c.login()
        stream = diaspy.streams.Stream(c)
        stream.update()

    def testGettingLength(self):
        c = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
        c.login()
        stream = diaspy.streams.Stream(c)
        stream.update()
        len(stream)

    def testClearing(self):
        stream = diaspy.streams.Stream(__connection__)
        stream.update()
        stream.clear()
        self.assertEqual(0, len(stream))

    def testPurging(self):
        stream = diaspy.streams.Stream(__connection__)
        post = stream.post('#diaspy test')
        stream.update()
        post.delete()
        stream.purge()
        self.assertNotIn(post.post_id, [post.post_id for post in stream])

    def testPostingText(self):
        c = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
        c.login()
        stream = diaspy.streams.Stream(c)
        post = stream.post('#diaspy test')
        self.assertEqual(diaspy.models.Post, type(post))

    def testPostingImage(self):
        c = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
        c.login()
        stream = diaspy.streams.Stream(c)
        stream.post_picture('./test-image.png')


class ConnectionTest(unittest.TestCase):
    def testLoginWithoutUsername(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, password='foo')

    def testLoginWithoutPassword(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, username='user')

    def testGettingUserInfo(self):
        connection = diaspy.connection.Connection(__pod__, __username__, __passwd__)
        connection.login()
        info = connection.getUserInfo()
        self.assertEqual(dict, type(info))


class ClientTests(unittest.TestCase):
    def testGettingStream(self):
        client = diaspy.client.Client(__pod__, __username__, __passwd__)
        stream = client.get_stream()
        if len(stream): self.assertEqual(diaspy.models.Post, type(stream[0]))

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


if __name__ == '__main__':
    unittest.main()
    c = diaspy.connection.Connection(__pod__, __username__, __passwd__)
    c.login()
    stream = diaspy.modules.Stream(c)
    for post in stream:
        if post['text'] == '#diaspy test': post.delete()
