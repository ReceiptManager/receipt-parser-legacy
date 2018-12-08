.PHONY: install
install:
	pipenv install

.PHONY: parse
parse:
	pipenv run python parser/parser.py

.PHONY: import
import:
	pipenv run python parser/importer.py

.PHONY: run
run: import parse

.PHONY: test
test:
	pipenv run pytest
