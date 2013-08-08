#!/usr/bin/env python3

import unittest

#   failure to import any of the modules below indicates failed tests
#   =================================================================
#   modules used by diaspy
import re
import requests
import warnings
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

print('Running tests on connection: "{0}:{1}@{2}"\t'.format(testconf.__username__, '*'*len(testconf.__passwd__), __pod__), end='')
test_connection = diaspy.connection.Connection(pod=__pod__, username=__username__, password=__passwd__)
test_connection.login()
print('[ CONNECTED ]\n')

post_text = '#diaspy test no. {0}'.format(test_count)


#######################################
####        TEST SUITE CODE        ####
#######################################
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
        self.assertEqual(diaspy.notifications.Notifications, type(notifications))
        if notifications: self.assertEqual(diaspy.models.Notification, type(notifications[0]))

    def testGettingTag(self):
        client = diaspy.client.Client(test_connection)
        tag = client.get_tag('foo')
        self.assertEqual(diaspy.streams.Generic, type(tag))
        if tag: self.assertEqual(diaspy.models.Post, type(tag[0]))

    def testGettingMailbox(self):
        client = diaspy.client.Client(test_connection)
        mailbox = client.get_mailbox()
        self.assertEqual(list, type(mailbox))
        self.assertEqual(diaspy.conversations.Conversation, type(mailbox[0]))


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
        self.assertNotIn(post.id, [p.id for p in stream])

    def testPostingText(self):
        stream = diaspy.streams.Stream(test_connection)
        post = stream.post(post_text)
        self.assertEqual(diaspy.models.Post, type(post))
    
    def testPostingImage(self):
        stream = diaspy.streams.Stream(test_connection)
        try:
            stream.post(text=post_text, photo='test-image.png')
        except (StreamError) as e:
            warnings.warn('{0}')
        finally:
            pass

    def testingAddingTag(self):
        ft = diaspy.streams.FollowedTags(test_connection)
        ft.add('test')

    def testAspectsAdd(self):
        aspects = diaspy.streams.Aspects(test_connection)
        aspects.add(testconf.test_aspect_name_fake)
        testconf.test_aspect_id = aspects.add(testconf.test_aspect_name).id

    def testAspectsGettingID(self):
        aspects = diaspy.streams.Aspects(test_connection)
        id = aspects.getAspectID(testconf.test_aspect_name)
        self.assertEqual(testconf.test_aspect_id, id)

    def testAspectsRemoveById(self):
        aspects = diaspy.streams.Aspects(test_connection)
        aspects.remove(testconf.test_aspect_id)
        self.assertEqual(-1, aspects.getAspectID(testconf.test_aspect_name))

    def testAspectsRemoveByName(self):
        aspects = diaspy.streams.Aspects(test_connection)
        aspects.remove(name=testconf.test_aspect_name_fake)
        self.assertEqual(-1, aspects.getAspectID(testconf.test_aspect_name_fake))

    def testActivity(self):
        activity = diaspy.streams.Activity(test_connection)

    def testMentionsStream(self):
        mentions = diaspy.streams.Mentions(test_connection)


class UserTests(unittest.TestCase):
    def testHandleSeparatorRaisingExceptions(self):
        handles = ['user.pod.example.com',
                   'user@podexamplecom',
                   '@pod.example.com',
                   'use r@pod.example.com',
                   'user0@pod300 example.com',
                   ]
        for h in handles:
            self.assertRaises(Exception, diaspy.people.sephandle, h)

    def testGettingUserByHandleData(self):
        user = diaspy.people.User(test_connection, handle=testconf.diaspora_id, fetch='data')
        self.assertEqual(testconf.guid, user['guid'])
        self.assertEqual(testconf.diaspora_id, user['handle'])
        self.assertEqual(testconf.diaspora_name, user['name'])
        self.assertEqual(type(user.stream), list)
        self.assertEqual(user.stream, [])
        self.assertIn('id', user.data)
        self.assertIn('avatar', user.data)

    def testGettingUserByHandlePosts(self):
        user = diaspy.people.User(test_connection, handle=testconf.diaspora_id)
        self.assertEqual(testconf.guid, user['guid'])
        self.assertEqual(testconf.diaspora_id, user['handle'])
        self.assertEqual(testconf.diaspora_name, user['name'])
        self.assertIn('id', user.data)
        self.assertIn('avatar', user.data)
        self.assertEqual(type(user.stream), diaspy.streams.Outer)
 
    def testGettingUserByGUID(self):
        user = diaspy.people.User(test_connection, guid=testconf.guid)
        self.assertEqual(testconf.diaspora_id, user['handle'])
        self.assertEqual(testconf.diaspora_name, user['name'])
        self.assertIn('id', user.data)
        self.assertIn('avatar', user.data)
        self.assertEqual(type(user.stream), diaspy.streams.Outer)


class ContactsTest(unittest.TestCase):
    def testGetOnlySharing(self):
        contacts = diaspy.people.Contacts(test_connection)
        result = contacts.get(set='only_sharing')
        for i in result:
            self.assertEqual(diaspy.people.User, type(i))

    def testGetAll(self):
        contacts = diaspy.people.Contacts(test_connection)
        result = contacts.get(set='all')
        for i in result:
            self.assertEqual(diaspy.people.User, type(i))

    def testGet(self):
        contacts = diaspy.people.Contacts(test_connection)
        result = contacts.get()
        for i in result:
            self.assertEqual(diaspy.people.User, type(i))


class PostTests(unittest.TestCase):
    def testStringConversion(self):
        s = diaspy.streams.Stream(test_connection)

    def testRepr(self):
        s = diaspy.streams.Stream(test_connection)


class NotificationsTests(unittest.TestCase):
    def testMarkgingRead(self):
        notifications = diaspy.notifications.Notifications(test_connection)
        notif = None
        for n in notifications:
            if n.unread:
                notif = n
                break
        if notif is not None:
            n.mark(unread=False)
        else:
            warnings.warn('test not sufficient: no unread notifications were found')

if __name__ == '__main__': 
    print('Hello World!')
    print('It\'s testing time!')
    n = unittest.main()
    print(n)
    print('It was testing time!')
