#### `Notifications()` object

In order to get list of notifications use `diaspy.notifications.Notifications()` object. 
It support iteration and indexing.

When creating new instance of `Notifications` only `Connection` object is needed.

#### Methods

##### `last()`

This method will return you last five notifications.

##### `get()`

This is slightly more advanced then `last()`. It allows you to specify how many 
notifications per page you want to get and which page you want to recieve.

----

#### `Notification()` model

Single notification (it should be obvious that it requires object of its own) is located in 
`diaspy.models.Notification()`. It has several methods you can use.

##### 1. `who()`

This method will return list of guids of the users who caused you to get this notification.

##### 2. `when()`

This method will return UTC time when you get the notification.

##### 3. `mark()`

To mark notification as `read` or `unread`. It has one parameter - `unread` which is boolean.

&nbsp;

Also, you can use `str()` and `repr()` on the `Notification()` and you will get nice 
string.

----

###### Manual for `diaspy`, written by Marek Marecki
