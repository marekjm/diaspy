#!/usr/bin/env python3


import time

from diaspy.models import Notification


"""This module abstracts notifications.
"""


class Notifications():
    """This class represents notifications of a user.
    """
    def __init__(self, connection):
        self._connection = connection
        self._data = {}
        self._notifications = self.get()
        self.page = 1

    def __iter__(self):
        return iter(self._notifications)

    def __getitem__(self, n):
        return self._notifications[n]

    def _finalise(self, notifications):
        self._data['unread_count'] = notifications['unread_count']
        self._data['unread_count_by_type'] = notifications['unread_count_by_type']
        return [Notification(self._connection, n) for n in notifications.get('notification_list', [])]

    def last(self):
        """Returns list of most recent notifications.
        """
        params = {'per_page': 5, '_': int(round(time.time(), 3)*1000)}
        headers = {'x-csrf-token': repr(self._connection)}

        request = self._connection.get('notifications.json', headers=headers, params=params)

        if request.status_code != 200:
            raise Exception('status code: {0}: cannot retreive notifications'.format(request.status_code))
        return self._finalise(request.json())

    def _expand(self, new_notifications):
        ids = [notification.id for notification in self._notifications]
        notifications = self._notifications
        data = self._data
        for n in new_notifications:
            if n.id not in ids:
                if n.unread:
                    data['unread_count'] +=1
					data['unread_count_by_type'][n.type] +=1
                notifications.append(n)
                ids.append(n.id)
        self._notifications = notifications
        self._data = data
        
    def _update(self, new_notifications):
        ids = [notification.id for notification in self._notifications]
        notifications = self._notifications
        data = self._data
        
        update = False
        if new_notifications[len(new_notifications)].id not in ids:
            update = True
        
        for i in range(len(new_notifications)):
            if new_notifications[-i].id not in ids:
                if new_notifications[-i].unread:
                    data[new_notifications[-i].type].unread_count +=1
                    data[new_notifications[-i].type].unread_count_by_type +=1
                notifications = [new_notifications[-i]] + notifications
                ids.append(new_notifications[-i].id)
        self._notifications = notifications
        self._data = data
        if update:
            self.update() # if there is a gap

    def update(self, per_page=5, page=1):
        result = self.get(per_page=per_page, page=page)
        if result:
            self._expand( result )
        
    def more(self, per_page=5, page=0):
        if not page: page = self.page + 1
        self.page = page
        result = self.get(per_page=per_page, page=page)
        if result:
            self._expand( result )

    def get(self, per_page=5, page=1):
        """Returns list of notifications.
        """
        params = {'per_page': per_page, 'page': page}
        headers = {'x-csrf-token': repr(self._connection)}

        request = self._connection.get('notifications.json', headers=headers, params=params)

        if request.status_code != 200:
            raise Exception('status code: {0}: cannot retreive notifications'.format(request.status_code))
        return self._finalise(request.json())
