#### `Post()` object and posting

`Post` object is used to represent a post on D\*.

#### Methods

##### `fetch()`

Use this method to get or update the post. As first parameter a `bool` 
can be given wich if is `True` will also fetch comments, default it 
won't.

##### `data()`

Set or get the current data for this post. If this method is called 
without any argument it will return a dict with the post data. To set 
post data for this post use the post data to set as first parameter 
(normaly you don't want to set this manualy).

##### `like()`

Likes this post.

##### `reshare()`

Reshares this post.

##### `comment()`

Comments on this post. First parameter a `str` with the text to comment.

##### `vote_poll()`

If the post contains a poll, you can vote on it by calling this method 
with as parameter the poll **answer** `id`.

##### `hide()`

Hides this post.

##### `mute()`

Blocks the post author.

##### `subscribe()`

Subscribes to this post (receive notifications on this post and its 
comments).

##### `unsubscribe()`

Unsubscribes from this post if you don't want to receive any 
notifications about this post anymore.

##### `report()`
This function is `TODO`, it doesn't work yet.

##### `delete()`

If you own this post you can delete it by calling this method.

##### `delete_comment()`

If you commented on this post and want to delete the comment call this 
method with as paramter the **comment** `id`.

##### `delete_like()`

If you liked this post you can call `delete_like()` to undo that.

##### `author()`

By default it returns the **author** `name`. As parameter you can give 
another key like **`id`**,  **`guid`**,  **`diaspora_id`** or 
**`avatar`**.

----

##### Posting

Posting is done through a `Stream` object method `post()`. 
It supports posting just text, images, a poll and a combination of those.

Additional you can set the provider name displayed in the post (wich can
 be your application it's name.) by setting the `provider_display_name` 
 parameter wich expects a `str`.

`Stream().post()` returns `Post` object referring to the post 
which have just been created.


##### Text

If you want to post just text you should call `post()` method with 
`text` argument.

    stream.post(text='Your post.')

It will return `Post` you have just created.

##### Poll

If you want to post a poll you have to provide the following:

* A `str` as the `poll_question` parameter wich will represent the poll 
question.
* A `list` with strings as the `poll_answers` parameter wich represent 
the poll options.

##### Posting images

Posting images, from back-end point of view, is a two-step process. 
First, you have to *upload* an image to the desired pod. 
This is done by `_photoupload()` method. 
It will return *id* of uploaded image. 

Then you have to actually post your image and this is done by appending 
`photos` field containg the id of uploaded image to the data being 
sent by request. This is handled by `post()` method. 

`post()` has two very similar arguments used for posting photos. 
They are `photos` - which takes id and `photo` - which takes filename. 

You can post images using either of them. Even passing them side by side
 is accepted but remember that `photos` will overwrite data set by 
 `photo`.


Example #1: using `photo`


    stream.post(photo='./kitten-image.png')


Example #2: using `photos`


    id = stream._photoupload(filename='./kitten-image.png')
    stream.post(photos=id)


The effect will be the same. 
To either call you can append `text` argument which will be posted 
alongside the image. 

----

###### Manual for `diaspy`, written by Marek Marecki
