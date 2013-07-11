#### `diaspy` models

Design of models in `diaspy` follow few simple rules.


##### Initialization

First argument is always `Connection` object stored in `self._connection`. 
Parameters specific to each model go after it.

If model requires some king of id (guid, conversation id, post id) it is simply `id`.
