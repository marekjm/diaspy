#### `Search()` object

Searching is useful only if it comes to searching for users or tags.

----

##### `lookup_user()`

This method is used for telling a pod "Hey, I want this user searchable 
via you!"

##### `user()`

This method will return you a list of dictionaries containg data of 
users whose handle conatins query you have used.

##### `tags()`

This method will return you a `list` with with `str`'s (tag names). As 
first parameter it expects a `str` representing the search phrase. The 
second parameter `limit` is optional, it can be set to increase or 
decrease the maximum returned results. The default for the `limit` 
parameter is `10`.
