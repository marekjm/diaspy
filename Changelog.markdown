## Changelog for `diaspy`, unofficla Diaspora\* API for Python

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

Version `0.3.2` (2013-08-):

* __upd__:  `diaspy.connection.getUserData()` raises `DiaspyError` when it cannot find user data,

* __rem__:  `diaspy.client.Client` must be explicitly imported,

----

Version `0.3.1` (2013-07-12):

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

Version `0.3.0` (2013-07-07):

First edition of Changelog for `diaspy`. 
Developers should update their code as version `0.3.0` may not be fully 
backwards compatible depending on how the code is written. 
If you always pass named arguments and do not rely on their order you can, at least in 
theory, not worry about this update. 

Version `0.3.0` introduces few new features, fixes several bugs and brings a bit of 
redesign and refactoring od `diaspy`'s code.

----
