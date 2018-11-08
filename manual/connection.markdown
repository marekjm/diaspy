#### `Connection()` object

This is the object that is used by `diaspy`'s internals. 
It is pushed around and used by various methods and other objects:

*   `Post()` and `Conversation()` objects require it to authenticate and 
    do their work,
*   streams use it for getting their contents,
*   etc.


`Connection()` is the most low-level part of `diaspy` and provides 
everything what is needed to talk to a pod.

However, using only `Connection()` would be hard and cumberstone so 
there are other modules to aid you and you are strongly encouraged to 
use them.


----

##### Login procedure

`Connection()`  will not log you in unless you explicitly order it to 
do so. Logging in with `Connection()` is done via `login()` method. 

**Example:**

    connection = diaspy.connection.Connection(pod='https://pod.example.com',
                                              username='user',
                                              password='password')
    connection.login()

----

##### Authentication

Authentication in Diaspora\* is done with *token*. It is a string 
which is passed to pod with several requests to prove you are who you 
are pretending to be.

`Connection` provides you with a method to fetch this token and perform 
various actions on your account.
This method is called `_fetchtoken()`. 
It will try to download a token for you. 

Once a token is fetched there is no use for doing it again. 
You can save time by using `get_token()` method. 
It will check whether the token had been already fetched and reuse it. 
This is especially useful on slow or unstable connections. 
`get_token()` has an optional `fetch` argument (it is of `bool` type, 
by default `False`) which will tell it to fetch new token if you find 
suitable.

However, recommended way of dealing with token is to use `repr()` 
function on `Connection` object. This will allow of your programs to be 
future-proof because if for any reason we will change the way in which 
authorization is handled `get_token()` method may be gone -- `repr()` 
will stay.

Here is how you should create your auth flow:

    connection = diaspy.connection.Connection(...)
    connection.login()

    token = repr(connection)


----

##### Note for developers

If you want to write your own interface or client for D\* 
`Connection()` is the only object you need.

----

###### Manual for `diaspy`, written by Marek Marecki
