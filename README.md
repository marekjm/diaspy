#### Python API for Diaspora (unofficial)

`diaspy` is a set of modules which form API for D\* social network. 
The API is written in Python 3.x and is not Python 2.x compatible. 

Object oriented design of `diaspy` makes it easily reusable by other 
developers who want to use only part of the API.

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


#### 2. More features

There is a special `client` module in diaspy which is an example client 
of D\* written using the `diapsy` API. It provides many features useful for 
interactions with social network like messages, mentions, likes etc. 
It is full of good, useful stuff.

----

To get more information about how the code works read 
documentation (`./doc/` directory) and manual (`./manual/` directory).
