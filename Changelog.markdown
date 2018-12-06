## Changelog for `diaspy`, unofficial DIASPORA\* interface for Python

This changelog file follows few rules:

*   __rem__:    indicates removed features,
*   __new__:    indicates new features,
*   __upd__:    indicates updated features,
*   __dep__:    indicates deprecated features,

Deprecation means that in the next version feature will be removed.

Also, after every version there should be a brief note describing possible 
problems with migrating to it from older versions and usage of new features. 

Users can always read the manual and dcumentation to make themselves more knowledgeable and 
are encouraged to do so. They only need to remember that documentation is usually more 
up-to-date than manual and if conflicts appear they should follow the order:

*docstrings* -> *docs/* -> *manual/*

----

#### Known issues

* __bug__:  `diaspy` has problems/can't connect to pods using SNI (this is an issue with requests/urllib3/python),


----

#### Version `0.6.1.dev` (not final changelog for this version, still in development)

* __upd__:  `diaspy.models.Post.like()`, `diaspy.models.Post.delete_like()`, `diaspy.models.Post.reshare()` will now update data (count and likes/reshares) without doing another request.

* __fix__:  `diaspy.models.Post.__init__()` checking on different fetch states was a mess.
* __fix__:  `diaspy.streams.Asepcts.filter()` location fix.

* __new__:  `diaspy.tagFollowings.TagFollowings()` which represents the tags followed by the user.
* __new__:  `diaspy.models.FollowedTag()` which represents a tag followed by the user. It is used by `diaspy.tagFollowings.TagFollowings()`.
* __new__:  It is now possible to give `**requestKwargs` to `diaspy.connection.Connection()` which will be used for every `request` unless directly overwritten by given the function you call different key-worded arguments.
* __new__:  `diaspy.connection.Connection()` now does check if the `pod` you are connecting to has `Camo` enabled or not. Call `diaspy.connection.Connection.camo()` to receive `True` or `False`.
* __new__:  `diaspy.models.Comment.authordata()` which will return all author data instead of `diaspy.models.Comment.author()` which will only return data for a certain key.
* __new__:  `diaspy.streams.Public()`
* __new__:  `diaspy.models.Post.fetchlikes()`.
* __new__:  `diaspy.models.Post.fetchreshares()`

* __rem__:  `diaspy.streams.FollowedTags.get()` since it wasn’t doing anything usefull.

* __dep__:  `diaspy.streams.FollowedTags.remove()` Use `diaspy.tagFollowings.TagFollowings[“tagName”].delete()` instead.
* __dep__:  `diaspy.streams.FollowedTags.add()` Use diaspy.tagFollowings.TagFollowings.follow() instead.


----


#### Version `0.6.0`

In this release some bugs due to Diaspora changes where adressed, it also 
contains some new functionality. Also if `BeautifulSoup4` is installed it 
will use it instead of the regex solution where possible. Also some manual 
adjustments.

IMPORTANT: `python-dateutil` is a requirement now.

Note: In this version indentation changed from spaces to tabs.


* __upd__:  `diaspy.people.User()`'s `fetchguid()` method can now be called with a parameter (`bool`), if set `False` it won't fetch the stream but only userdata, default it still does.,
* __upd__:  `diaspy.people.User()` has new methods `getPhotos()` and `deletePhoto()`,
* __upd__:  Aspect `id` is now removed from `diaspy.people.User()` object when removed,
* __upd__:  `diaspy.people.Contacts()` it's `get()` method has the `page` parameter now,
* __upd__:  It is now optional to automatic fetch contacts for `diaspy.people.Contacts()`, default it won't,
* __upd__:  `diaspy.models.Notification()`'s `who()` method now return whole `guid`s instead of partial `guid`s,
* __upd__:  Update `diaspy.models.Post()` it's interaction data after liked,
* __upd__:  `diaspy.connection.Connection()`'s `getUserData()` method will now set the `Connection()` object it's `self._userdata`,
* __upd__:  Posts obtained by `diaspy.streams.Generic()` are now fetched once instead of twice,
* __upd__:  `tests.py`,


* __fix__:  Streams seemed to miss posts on `more()` method, should be fixed now. Also a new dependency: `dateutil`,
* __fix__:  Fixes `diaspy.streams.Generic()`'s `more()` and `update()` methods and adds `id` to posts,
* __fix__:  `diaspy.streams.Aspect()` its `filter()` method,
* __fix__:  `diaspy.models.Notification()`'s `who()` method it's regex pattern didn't always match, now it should,
* __fix__:  `diaspy.models.Aspect()` its `addUser()` method did cause CSRF errors,
* __fix__:  `diaspy.people.User()` its `getHCard()`,


* __new__:  `diaspy.errors.SearchError()` and `diaspy.errors.TagError()`,
* __new__:  `update()` and `more()` methods for `diaspy.notifications.Notifications`,
* __new__:  `removeAspect()` method in `diaspy.models.Aspect()`,
* __new__:  `diaspy.models.Comments()` class,
* __new__:  `diaspy.models.Conversation()` has new methods `messages()` and `update_messages()`, it is also posible to call `len()` and iterate over the object,
* __new__:  `diaspy.models.Post()`'s `comments` object is now a `Comments()` object instead of a `dict` (parsed json),
* __new__:  `diaspy.models.Post()` has some new methods: `vote_poll()`, `hide()`, `mute()`, `subscribe()` and `unsubscribe()`,
* __new__:  It is now possible to set `diaspy.people.User()` it's data manual by the `data` parameter,
* __new__:  `diaspy.people.Contacts()` has new methods `add()` and `remove()` wich can add/remove a user to/from an aspect,
* __new__:  Added BeautifulSoup4 (optional) support where possible instead of regex, kept regex as fallback,
* __new__:  `diaspy.connection.Connection().podswitch()` has now a optional param `login` with as default set to `True`, if `False` it will only set the data and does not call `login()`,


* __rem__:  `_obtain()` from `diaspy.streams.Outer()`, it was the same as `_obtain()` in `diaspy.streams.Generic()`,
* __rem__:  `diaspy.models.Post()` its `update()` method since it is deprecated for a while now,
* __rem__:  `backtime` parameter removed from `diaspy.streams.Generic.more()`,
* __rem__:  `protocol` parameter removed from `diaspy.people.User().fetchhandle()`.


----


#### Version `0.5.0.1`

This is a hotfix release.
Plain 0.5.0 lost compatibility with older versions of Diaspora* due to a trivial assignment-related bug.


----

#### Version `0.5.0`

Release 0.5.0
This release fixes a bug that arose with Diaspora* 0.5.0 update which
changed the way how the CSRF tokens have been embedded in HTML code.
This required minor fix to the CSRF-extracting regex.

Not much besides. Fixed a typo or two.


----

#### Version `0.4.3`:

* __new__:  `people.User().fetchprofile()` will issue a warning when user cannot be found on current pod,
* __new__:  `settings.Profile` is now loaded during initialization (can be switched off),

* __fix__:  fixed a bug in `__repr__()` method in `people.User()` object,


----

#### Version `0.4.2` (2013-12-19):

This version has some small incompatibilities with `0.4.1` so read Changelog carefully.

* __new__:  `diaspy.people.User._fetchstream()` method,
* __new__:  `diaspy.people.Me()` object representing current user,
* __new__:  `**kwargs` added to `diaspy.streams.Generic.json()` methdo to give developers control over the creation of JSON,
* __new__:  `.getHCard()` method added to `diaspy.people.User()`,


* __upd__:  `diaspy.connection.Connection.login()` modifies connection object in-place **and** returns it (this allows more fluent API),
* __upd__:  `diaspy.connection.Connection.login()` no longer returns status code (if login was unsuccessful it'll raise an exception),
* __upd__:  `diaspy.connection.Connection._login()` no longer returns status code (if login was unsuccessful it'll raise an exception),
* __upd__:  better error message in `diaspy.models.Post().__init__()`,
* __upd__:  `data` variable in `diaspy.models.Post()` renamed to `_data` to indicate that it's considered private,
* __upd__:  after deleting a post `Activity` stream is purged instead of being refilled (this preserves state of stream which is not reset to last 15 posts),
* __upd__:  `filterByIDs()` method in `Aspects` stream renamed to `filter()`,


* __rem__:  `diaspy.connection.Connection.getUserInfo()` moved to `diaspy.connection.Connection.getUserData()`,
* __rem__:  `fetch` parameter removed from `diaspy.connection.Connection.getUserData()`,


* __dep__:  `max_time` parameter in `diaspy.streams.*.more()` method is deprecated,

* __fix__:  this release should fix the bug which prevented diaspy from working with some pods (e.g. diasp.eu and joindiaspora.com),


----

#### Version `0.4.1` (2013-09-12):

Login and authentication procedure backend received major changes in this version.
There are no longer `username` and `password` variables in `Connection` object.
Instead, credentials are stored (together with the token) in single variable `_login_data`.
This is preserved until you call `login()` at which point credentials are erased and
only token is left -- it can be obtained by calling `repr(Connection)`.

Also, this release is compatible with DIASPORA\* 0.2.0.0 but should still support
pods running on older versions.

And the test suite was updated. Yay!


* __new__:  `diaspy.errors.SettingsError`.


* __upd__:  `diaspy.settings.Account.setEmail()` can now raise `SettingsError` when request fails,
* __upd__:  `diaspy.settings.Account.getEmail()` will now return empty string instead of raising an exception if cannot fetch mail,
* __upd__:  improved language fetching in `diaspy.settings.Account.getLanguages()`.


* __rem__:  `diaspy/client.py` is removed,


**`0.4.1-rc.3` (2013-09-08):**

* __new__:  `diaspy.settings.Profile.load()` method for loading profile information,
* __new__:  `diaspy.settings.Profile.update()` method for updating profile information,
* __new__:  `diaspy.settings.Profile.setName()` method,
* __new__:  `diaspy.settings.Profile.setBio()` method,
* __new__:  `diaspy.settings.Profile.setLocation()` method,
* __new__:  `diaspy.settings.Profile.setTags()` method,
* __new__:  `diaspy.settings.Profile.setGender()` method,
* __new__:  `diaspy.settings.Profile.setBirthDate()` method,
* __new__:  `diaspy.settings.Profile.setSearchable()` method,
* __new__:  `diaspy.settings.Profile.setNSFW()` method,


**`0.4.1-rc.2` (2013-09-06):**

* __new__:  `diaspy.search.Search.tags()` method for getting tag suggestions,
* __new__:  `diaspy.settings.Profile.getName()` method,
* __new__:  `diaspy.settings.Profile.getBio()` method,
* __new__:  `diaspy.settings.Profile.getLocation()` method,
* __new__:  `diaspy.settings.Profile.getTags()` method,
* __new__:  `diaspy.settings.Profile.getGender()` method,
* __new__:  `diaspy.settings.Profile.getBirthDate()` method,
* __new__:  `diaspy.settings.Profile.isSearchable()` method,
* __new__:  `diaspy.settings.Profile.isNSFW()` method,
* __new__:  `provider_display_name` parameter in `diaspy.streams.Stream.post()` (thanks @svbergerem),


* __upd__:  `remeber_me` parameter in `diaspy.connection.Connection.login()`,
* __upd__:  you must supply `username` and `password` parameters on init of `diaspy.connection.Connection`,
* __upd__:  you must update your testconf.py (new fields are required for settings tests),
* __upd__:  `diaspy.settings.Settings` renamed to `diaspy.settings.Account`,


* __rem__:  `username` and `password` parameters removed from `diaspy.connection.Connection.login()`
            must be supplied on init,


**`0.4.1-rc.1` (2013-09-02):**

* __new__:  `__getitem__()` in `diaspy.models.Post`,
* __new__:  `__dict__()` in `diaspy.models.Post`,
* __new__:  `guid` argument in `diaspy.models.Post.__init__()`,
* __new__:  `json()` method in `diaspy.streams.Generic` adds the possibility to export streams to JSON,
* __new__:  `full()` method in `diaspy.streams.Generic` will try to fetch full stream (containing all posts),
* __new__:  `setEmail()` method in `diaspy.settings.Settings`,
* __new__:  `setLanguage()` method in `diaspy.settings.Settings`,
* __new__:  `downloadPhotos()` method in `diaspy.settings.Settings`,
* __new__:  `backtime` argument in `more()` method in `diaspy.streams.Generic`,
* __new__:  `DiaspyError` will be raised when connection is created with empty password and/or username,
* __new__:  `getSessionToken()` method in `diaspy.connection.Connection` returns string from `_diaspora_session` cookie,
* __new__:  `direct` parameter in `diaspy.connection.Connection().get()` allowing to disable pod expansion,


* __upd__:  if `Post()` is created with fetched comments, data will also be fetched as a dependency,
* __upd__:  `id` argument type is now `int` (`diaspy.models.Post.__init__()`),
* __upd__:  `Search().lookup_user()` renamed to `Search().lookupUser()`,
* __upd__:  `diaspy.messages` renamed to `diaspy.conversations` (but will be accessible under both names for this and next release),
* __upd__:  `LoginError` moved to `diaspy.errors`,
* __upd__:  `TokenError` moved to `diaspy.errors`,
* __upd__:  `diaspy.connection.Connection.podswitch()` gained two new positional arguments: `username` and `password`,
* __upd__:  `aspect_id` renamed to `id` in `diaspy.streams.Aspects().remove()`,


* __fix__:  fixed some bugs in regular expressions used by `diaspy` internals (html tag removal, so you get nicer notifications),
* __fix__:  fixed authentication issues,


----

#### Version `0.4.0` (2013-08-20):

This release is **not backwards compatible with `0.3.x` line**! You'll have to check your code for corrections.
Also, this release if first to officially released fork version.

* __dep__:  `diaspy.client` is officially deprecated (will be removed in `0.4.1`),


* __upd__:  `diaspy.conversations` renamed to `diaspy.messages`,
* __udp__:  `diaspy.conversations.Conversation` moved to `diaspy.models`,


* __new__:  `diaspy.messages.Mailbox()` object representing diaspora\* mailbox,

----

#### Version `0.3.2` (2013-08-20):

* __upd__:  `diaspy.connection.getUserData()` raises `DiaspyError` when it cannot find user data,


* __rem__:  `diaspy.client.Client` must be explicitly imported,

----

#### Version `0.3.1` (2013-07-12):

* __upd__:  `diaspy.people.sephandle()` raises `InvalidHandleError` instead of `UserError`
* __upd__:  `models.Post()._fetch()` renamed to `_fetchdata()` (because of new `_fetchcomments()` method)


* __new__:  `models.Comment()` object: wrapper for comments, not to be created manually
* __new__:  `comments` parameter in `models.Post`: defines whether to fetch post's commets
* __new__:  `connection.Connection` has new parameter in `__init__()`: it's `schema`
* __new__:  `author()` method in `models.Post()`


The new parameter in `connection.Connection` is useful when operating with handles. 
As handle does not contain schema (`http`, `https`, etc.) `_setlogin()` would raise an 
unhandled exception -- `requests.exceptions.MissingSchema`. 
Now, however, `Connection` will catch the exception, add missing schema and try once more. 
This parameter is provided to give programmers ability to manipulate it. 

Also, now you can pass just `pod.example.com` as `pod` parameter. Less typing!

When it comes to posts, we are now able to fetch comments.

----

#### Version `0.3.0` (2013-07-07):

First edition of Changelog for `diaspy`. 
Developers should update their code as version `0.3.0` may not be fully 
backwards compatible depending on how the code is written. 
If you always pass named arguments and do not rely on their order you can, at least in 
theory, not worry about this update. 

Version `0.3.0` introduces few new features, fixes several bugs and brings a bit of 
redesign and refactoring od `diaspy`'s code.

&nbsp;
