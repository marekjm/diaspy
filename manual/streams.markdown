#### `Stream()` object

This object is used to represent user's stream on D\*. 
It is returned by `Client()`'s method `get_stream()` and 
is basically a list of posts. 

----

##### Getting stream

To get basic stream you have to have working `Connection()` as 
this is required by `Stream()`'s constructor.

    c = diaspy.connection.Connection(pod='https://pod.example.com',
                                     username='foo',
                                     password='bar')
    c.login()
    stream = diaspy.models.Stream(c)

Now you have a stream filled with posts (if any can be found on user's stream).

----

##### `fill()`, `update()` and `more()`

When you want to refresh stream call it's `fill()` method. It will overwrite old stream 
contents.

On the contrary, `update()` will get a new stream but will not overwrite old stream saved 
in the object memory. It will append every new post to the old stream.

`more()` complements `update()` it will fetch you older posts instead of newer ones.

----

##### Length of and iterating over a stream

Stream's length can be checked by calling `len()` on it.

    len(stream)
    10

When you want to iterate over a stream (e.g. when you want to print first *n* posts on 
the stream) you can do it in two ways.

First, using `len()` and `range()` functions.

    for i in range(len(stream)):
        # do stuff...

Second, iterating directly over the stream contents:

    for post in stream:
        # do stuff...


----

##### Posting data to stream

This is described in [`posting`](./posting.mdown) document in this manual.


----

##### Clearing stream

##### `clear()`

This will remove all posts from visible stream.

##### `purge()`

This will scan stream for nonexistent posts (eg. deleted) and remove them.

----

###### Manual for `diaspy`, written by Marek Marecki
