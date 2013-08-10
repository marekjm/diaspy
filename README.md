#### Unofficial Python interface for Diaspora\* social network

`diaspy` is a set of modules which form an Python interface to the API of
Disapora\* social network. 

Test suite will cause problems when run with 2.x so testing should be done 
using python3 interpreter.

Object oriented design of `diaspy` makes it easily reusable by other 
developers who want to use only part of the interface and create derivative
works from it.

Developrs who don't like the design of `diaspy` and want to create something better
can use only `diaspy.connection.Connection()` object as it is capable of
doing everything. Other modules are just layers that provide easier access to
parts of the Diaspora\* API.

----

#### Quick intro

#### 1. Posting text to your stream

You only need two objects to do this: `Stream()` and `Connection()`. 

    >>> import diaspy
    >>> c = diaspy.connection.Connection(pod='https://pod.example.com',
    ...                                  username='foo',
    ...                                  password='bar')
    >>> c.login()
    >>> stream = diaspy.models.Stream(c)
    >>> stream.post('Your first post')


#### 2. Reference implementation

There is no official reference implementation of D\* client using `diaspy`.
The `diaspy.client` module is no longer maintained and will be removed in the future.

However, there is a small script written that uses `diaspy` as its backend.
Look for `diacli` in marekjm's repositories on GitHub.

----

To get more information about how the code works read 
documentation (`./doc/` directory) and manual (`./manual/` directory).
