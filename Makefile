.PHONY: test cov

cov:
	poetry run coverage run -m pytest
	poetry run coverage report

test:
	poetry run pytest
