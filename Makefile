.PHONY: tests

tests:
	python3 -m unittest --verbose --catch --failfast tests.py
