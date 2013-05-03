#!/usr/bin/env python3

import unittest

#   failure to import any of the modules below indicates failed tests
#   modules used by diaspy
import requests
import re
#   actual diaspy code
import diaspy


####    SETUP STUFF
####    test suite configuration variables: can be adjusted to your liking
import testconf
__pod__ = testconf.__pod__
__username__ = testconf.__username__
__passwd__ = testconf.__passwd__


# Test counter
try:
    test_count_file = open('TEST_COUNT', 'r')
    test_count = int(test_count_file.read())
    test_count_file.close()
except (IOError, ValueError):
    test_count = 0
finally:
    test_count += 1
test_count_file = open('TEST_COUNT', 'w')
test_count_file.write(str(test_count))
test_count_file.close()
print('Running test no. {0}'.format(test_count))

print('Running tests on connection to pod: "{0}"\t'.format(__pod__), end='')
test_connection = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
test_connection.login()
print('[ CONNECTED ]\n')


#### Test suite code
class StreamTest(unittest.TestCase):
    def testGetting(self):
        stream = diaspy.streams.Generic(test_connection)

    def testGettingLength(self):
        stream = diaspy.streams.Generic(test_connection)
        len(stream)

    def testClearing(self):
        stream = diaspy.streams.Stream(test_connection)
        stream.clear()
        self.assertEqual(0, len(stream))

    def testPurging(self):
        stream = diaspy.streams.Stream(test_connection)
        post = stream.post('#diaspy test')
        stream.update()
        post.delete()
        stream.purge()
        self.assertNotIn(post.post_id, [p.post_id for p in stream])

    def testPostingText(self):
        stream = diaspy.streams.Stream(test_connection)
        post = stream.post('#diaspy test no. {0}'.format(test_count))
        self.assertEqual(diaspy.models.Post, type(post))

    def testPostingImage(self):
        stream = diaspy.streams.Stream(test_connection)
        stream.post_picture('./test-image.png')


class ConnectionTest(unittest.TestCase):
    def testLoginWithoutUsername(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, password='foo')

    def testLoginWithoutPassword(self):
        connection = diaspy.connection.Connection(pod=__pod__)
        self.assertRaises(diaspy.connection.LoginError, connection.login, username='user')

    def testGettingUserInfo(self):
        info = test_connection.getUserInfo()
        self.assertEqual(dict, type(info))


class ClientTests(unittest.TestCase):
    def testGettingStream(self):
        client = diaspy.client.Client(test_connection)
        stream = client.get_stream()
        if len(stream): self.assertEqual(diaspy.models.Post, type(stream[0]))

    def testGettingNotifications(self):
        client = diaspy.client.Client(test_connection)
        notifications = client.get_notifications()
        self.assertEqual(list, type(notifications))
        if notifications: self.assertEqual(dict, type(notifications[0]))

    def testGettingTagAsList(self):
        client = diaspy.client.Client(test_connection)
        tag = client.get_tag('foo')
        self.assertEqual(list, type(tag))
        if tag: self.assertEqual(diaspy.models.Post, type(tag[0]))

    def testGettingTagAsStream(self):
        client = diaspy.client.Client(test_connection)
        tag = client.get_tag('foo', stream=True)
        self.assertEqual(diaspy.streams.Generic, type(tag))
        if tag: self.assertEqual(diaspy.models.Post, type(tag[0]))

    def testGettingMailbox(self):
        client = diaspy.client.Client(test_connection)
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
