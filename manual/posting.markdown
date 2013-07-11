#### `Post()` object and posting

`Post` object is used to represent a post on D\*.

----

##### Posting

Posting is done through a `Stream` object method `post()`. 
It supports posting just text, images or text and images.

`Stream().post()` returns `Post` object referring to the post 
which have just been created.


##### Text

If you want to post just text you should call `post()` method with 
`text` argument.

    stream.post(text='Your post.')

It will return `Post` you have just created.


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
is accepted but remember that `photos` will overwrite data set by `photo`.


Example #1: using `photo`


    stream.post(photo='./kitten-image.png')


Example #2: using `photos`


    id = stream._photoupload(filename='./kitten-image.png')
    stream.post(photos=id)


The effect will be the same. 
To either call you can append `text` argument which will be posted alongside 
the image. 

----

###### Manual for `diaspy`, written by Marek Marecki
