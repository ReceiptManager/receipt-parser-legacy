.PHONY: install
install:
	pipenv install

.PHONY: parse
parse:
	pipenv run python -m parser

.PHONY: import
import:
	pipenv run python parser/importer.py

.PHONY: run
run: import parse

.PHONY: docker-build
docker-build:
	docker build -t mre0/receipt-parser .	

.PHONY: docker-run
docker-run:
	docker run -v `pwd`/data/img:/usr/src/app/data/img mre0/receipt-parser

.PHONY: test
test:
	pipenv run pytest

.PHONY: clean
clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
