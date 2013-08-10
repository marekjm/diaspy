#!/usr/bin/env python3

"""Script for downloading all user data.

Named after SensualAsaCat user whose account was deleted after some
radikal transgender reported her to admins of joindiaspora.com for
posting *inappropriate* content.

I disaggred with him. So, here it is get all SensualAsaCat's pictures.
"""

import getpass
import urllib.request

import diaspy


guid = "b1b7d3e76ec50c7d"

pod = input('Your pod: ')
username = input ('Your username on pod \'{0}\': '.format(pod))
password = getpass.getpass('Password for \'{0}@{1}\': '.format(username, pod))

connection = diaspy.connection.Connection(pod=pod, username=username, password=password)
connection.login()


user = diaspy.people.User(connection, guid=guid)

oldstream = user.stream.copy()
user.stream.more()

while len(oldstream) != len(user.stream):
    try:
        oldstream = user.stream.copy()
        user.stream.more()
        go = True
    except KeyboardInterrupt:
        go = False
    finally:
        if go: print('Working... ({0})'.format(len(oldstream)))

print('Posts found:', len(user.stream))
for i, p in enumerate(oldstream):
    print(repr(p))
    if p.data['photos']:
        print('Downloading photos...')
        for n, photo in enumerate(p.data['photos']):
            print('{0}/{1}'.format(n+1, len(p.data['photos'])), end='\t')
            try:
                name = photo['guid'] + photo['sizes']['large'].split('.')[-1]
                urllib.request.urlretrieve(url=photo['sizes']['large'], filename=name)
                print('[  OK  ]')
            except Exception as e:
                print('[ FAIL: {0}]'.format(e))
            finally:
                pass
    print('\n\n----\n')
