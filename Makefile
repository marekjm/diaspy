.PHONY: style-check test

style-check:
	flake8 --max-complexity 6 ./diaspy/

test:
	python3 -m unittest --verbose --catch --failfast tests.py
