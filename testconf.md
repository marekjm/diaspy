##  Configuration file for `diaspy` test suite (./tests.py)

Developer/tester has to create their own `testconf.py` file 
because it is appended to `.gitignore` to avoid accidental 
posting of personal data (passsword for D*).


#### You have to set the variables yourself!
#### Their values have to be valid!

Template file:

    __pod__ = 'https://pod.example.com'
    __username__ = 'user'
    __passwd__ = 'strong_password'
    diaspora_id = 'user@pod.example.com'
    guid = '12345678abcdefgh'
    # your name as others see it
    diaspora_name = 'Marek Marecki'

    #   both names are created
    test_aspect_name = 'diaspy-test'
    #   but this one will be deletd `by name`
    test_aspect_name_fake = 'diaspy-test-fake'

    #   needed here for tests to work
    test_aspect_id = -1
