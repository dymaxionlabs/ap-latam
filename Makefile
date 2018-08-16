.PHONY: test cov

cov:
	coverage run -m pytest
	coverage report
	coverage html

test:
	pytest

build_image:
	docker build -t dymaxionlabs/ap-latam:latest .
