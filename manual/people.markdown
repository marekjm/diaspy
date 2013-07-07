#### `User()` object

This object is used to represent a D\* user.

----

##### `User()` object -- getting user data

You have to know either GUID or *handle* of a user. 
Assume that *1234567890abcdef* and *otheruser@pod.example.com* point to 
the same user.

    >>> c = diaspy.connection.Connection('https://pod.example.com', 'foo', 'bar')
    >>> 
    >>> user_guid = diaspy.people.User(c, guid='1234567890abcdef')
    >>> user_handle = diaspy.people.User(c, handle='otheruser@pod.example.com')

Now, you have two `User` objects containing the data of one user.

The object is subscriptable so you can do like this:

    >>> user_guid['handle']
    'otheruser@pod.example.com'
    >>> 
    >>> user_handle['guid']
    '1234567890abcdef'

`User` object contains following items in its `data` dict:

* `id`, `str`, id of the user;
* `guid`, `str`, guid of the user;
* `handle`, `str`, D\* id (or handle) of the user;
* `name`, `str`, name of the user;
* `avatar`, `dict`, links to avatars of the user;

>   **Historical note:** the above values were changed in version `0.3.0`.  
>   `diaspora_id` became `handle` and `image_urls` became `avatar` to have more
>   consistent results.
>   This is because we can get only user data and this returns dict containing 
>   `handle` and `avatar` and not `diaspora_id` and `image_urls`. 
>   Users who migrated from version `0.2.x` and before to version `0.3.0` had to
>   update their software.

Also `User` object contains a stream for this user.

* `stream`, `diaspy.streams.Outer`, stream of the user (provides all methods of generic stream);

====


#### `Contacts()` object

This is object abstracting list of user's contacts. 
It may be slightly confusing to use and reading just docs could be not enough. 

The only method of this object is `get()` and its only parameter is `set` which 
is optional (defaults to empty string).  
If called without specifying `set` `get()` will return list of users (`User` objects) 
who are in your aspects.

Optional `set` parameter can be either `all` or `only_sharing`. 
If passed as `only_sharing` it will return only users who are not in your aspects but who share 
with you - which means that you are in their aspects.
If passed as `all` it will return list of *all* your contacts - those who are in your aspects and 
those who are not.


To sum up: people *who you share with* are *in* your aspects. People *who share with you* have you in 
their aspects. These two states can be mixed.


----

###### Manual for `diaspy`, written by Marek Marecki
