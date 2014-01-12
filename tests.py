#!/usr/bin/env python3

from __future__ import print_function

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

# Setup test aspects
print('Adding test aspects...\t', end='')
diaspy.streams.Aspects(test_connection).add(testconf.test_aspect_name_fake)
testconf.test_aspect_id = diaspy.streams.Aspects(test_connection).add(testconf.test_aspect_name).id
print('OK')

print([i['name'] for i in test_connection.getUserData()['aspects']])


post_text = '#diaspy test no. {0}'.format(test_count)


#######################################
####        TEST SUITE CODE        ####
#######################################
class ConnectionTest(unittest.TestCase):
    def testGettingUserInfo(self):
        info = test_connection.getUserData()
        self.assertEqual(dict, type(info))


class MessagesTests(unittest.TestCase):
    def testGettingMailbox(self):
        mailbox = diaspy.messages.Mailbox(test_connection)
        if mailbox: 
            for i in range(len(mailbox)):
                self.assertEqual(diaspy.models.Conversation, type(mailbox[i]))


class AspectsTests(unittest.TestCase):
    def testAspectsGettingID(self):
        aspects = diaspy.streams.Aspects(test_connection)
        id = aspects.getAspectID(testconf.test_aspect_name)
        self.assertEqual(testconf.test_aspect_id, id)

    def testAspectsRemoveById(self):
        aspects = diaspy.streams.Aspects(test_connection)
        for i in test_connection.getUserData()['aspects']:
            if i['name'] == testconf.test_aspect_name:
                print(i['id'], end=' ')
                aspects.remove(id=i['id'])
                break
        names = [i['name'] for i in test_connection.getUserData()['aspects']]
        print(names)
        self.assertNotIn(testconf.test_aspect_name, names)

    def testAspectsRemoveByName(self):
        aspects = diaspy.streams.Aspects(test_connection)
        print(testconf.test_aspect_name_fake, end=' ')
        aspects.remove(name=testconf.test_aspect_name_fake)
        names = [i['name'] for i in test_connection.getUserData()['aspects']]
        print(names)
        self.assertNotIn(testconf.test_aspect_name_fake, names)


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
        except (diaspy.errors.StreamError) as e:
            warnings.warn('{0}')
        finally:
            pass

    def testingAddingTag(self):
        ft = diaspy.streams.FollowedTags(test_connection)
        ft.add('test')

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

    def testReprMethod(self):
        user = diaspy.people.User(test_connection, guid=testconf.guid)
        repr(user)
        print(user)


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
    def testMarkingRead(self):
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


class SettingsTests(unittest.TestCase):
    profile = diaspy.settings.Profile(test_connection)
    account = diaspy.settings.Account(test_connection)

    def testGettingName(self):
        self.assertEqual(testconf.user_names_tuple, self.profile.getName())

    def testGettingLocation(self):
        self.assertEqual(testconf.user_location_string, self.profile.getLocation())

    def testGettingGender(self):
        self.assertEqual(testconf.user_gender_string, self.profile.getGender())

    def testGettingBirthDate(self):
        self.assertEqual(testconf.user_date_of_birth, self.profile.getBirthDate(named_month=False))
        self.assertEqual(testconf.user_date_of_birth_named, self.profile.getBirthDate(named_month=True))

    def testGettingInfoIfProfileIsSearchable(self):
        self.assertEqual(testconf.user_is_searchable, self.profile.isSearchable())

    def testGettingInfoIfProfileIsNSFW(self):
        self.assertEqual(testconf.user_is_nsfw, self.profile.isNSFW())

    def testGettingTags(self):
        self.assertEqual(sorted(testconf.user_tags), sorted(self.profile.getTags()))

    def testGettingLanguages(self):
        self.assertIn(('en', 'English'), self.account.getLanguages())

    def testGettingEmail(self):
        self.assertEqual(testconf.user_email, self.account.getEmail())


if __name__ == '__main__': 
    print('Hello World!')
    print('It\'s testing time!')
    n = unittest.main()
    print(n)
    print('Good! All tests passed!')
