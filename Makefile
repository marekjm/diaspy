.PHONY: style-check test

style-check:
	flake8 ./diaspy/

test:
	python3 -m unittest --verbose --catch --failfast tests.py
