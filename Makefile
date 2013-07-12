.PHONY: style-check test

style-check:
	flake8 --max-complexity 6 ./diaspy/

test:
	python3 -m unittest --verbose --catch --failfast tests.py

test-python2:
	python2 -m unittest --verbose --catch --failfast tests.py

clean:
	rm -rv diaspy/__pycache__/
	rm -rv diaspy/*.pyc
	rm -rv ./__pycache__/
	rm -rv *.pyc

install:
	python setup.py install
	rm -rvf dist/
	rm -rvf diaspy.egg-info
