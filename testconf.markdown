##  Configuration file for `diaspy` test suite (./tests.py)

Developer/tester has to create their own `testconf.py` file 
because it is appended to `.gitignore` to avoid accidental 
upload of personal data.


#### You have to set the variables yourself!
#### Their values have to be valid!

Template file:

    #   Here is a configuration file for test suite for diaspy.
    #   Fill it with correct data.
    #   
    #   Fields are explained in testconf.md file.


    # Your login details
    __pod__ = 'https://pod.orkz.net'
    __username__ = 'marekjm'
    __passwd__ = 'mAreKJmonDiASporA'


    # D* identifiers
    diaspora_id = 'marekjm@pod.orkz.net'
    guid = 'fd4ac447f2d267fa'


    # Details of your account
    diaspora_name = 'Marek Marecki'
    user_names_tuple = ('Marek', 'Marecki')
    user_location_string = 'Poland'
    user_gender_string = 'Dude'
    user_date_of_birth = (1995, 3, 22)
    # remember about language you've set!
    user_date_of_birth_named = (1995, 'March', 22)
    user_is_searchable = True
    user_is_nsfw = False


    # both names are created
    test_aspect_name = 'diaspy-test'

    # but this one will be deletd `by name`
    test_aspect_name_fake = 'diaspy-test-fake'

    # don't change needed for tests to work
    test_aspect_id = -1
