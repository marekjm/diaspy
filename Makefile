.PHONY: style-check test

style-check:
	flake8 --max-complexity 6 ./diaspy/

test:
	python3 -m unittest --verbose --catch --failfast tests.py

test-python2:
	python2 -m unittest --verbose --catch --failfast tests.py

clean:
	rm -rv {*/,}__pycache__/
	rm -rv {*/,}*.pyc
