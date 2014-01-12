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
