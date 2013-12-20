.PHONY: style-check test

style-check:
	flake8 --max-complexity 6 ./diaspy/

test:
	python3 -m unittest --verbose --catch --failfast tests.py

test-python2:
	python2 -m unittest --verbose --catch --failfast tests

clean:
	rm -v ./{diaspy/,}*.pyc
	rm -rv ./{diaspy/,}__pycache__/

install:
	python setup.py install
	rm -rvf dist/
	rm -rvf diaspy.egg-info
