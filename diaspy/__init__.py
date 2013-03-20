import diaspy.client
import diaspy.models
import diaspy.conversations

class Client(diaspy.client.Client):
    """Class created for easier imports of client. 
    Instead of:

        import diaspy
        client = diaspy.client.Client(...)

    you can simply use:

        import diaspy
        client = diaspy.Client(...)

    """
    pass
