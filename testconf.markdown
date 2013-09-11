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
    __pod__ = 'https://pod.example.com'
    __username__ = 'user'
    __passwd__ = 'password'


    # D* identifiers
    diaspora_id = 'user@pod.example.com'
    guid = 'abcdef01234678'


    # Details of your account
    diaspora_name = 'Foo Bar'
    user_names_tuple = ('Foo', 'Bar')
    user_email = 'email@example.com'
    user_location_string = 'Nowhere'
    user_gender_string = 'Gender'
    user_date_of_birth = (2013, 9, 7)
    # remember about language you've set!
    user_date_of_birth_named = (2013, 'September', 7)
    user_is_searchable = True
    user_is_nsfw = False
    # five tags you use to describe yourself (all in lowercase)
    user_tags = ['movies', 'kittens', 'travel', 'teacher', 'newyork']


    # both names are created
    test_aspect_name = 'diaspy-test'

    # but this one will be deletd `by name`
    test_aspect_name_fake = 'diaspy-test-fake'

    # don't change needed for tests to work
    test_aspect_id = -1
