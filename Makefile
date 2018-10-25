
lint:
	pylint src tests
	flake8 src tests

test:
	nose2 -v tests.api_testing --with-coverage
