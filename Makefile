.PHONY: install
install:
	pipenv install

.PHONY: parse
parse:
	pipenv run python $(PWD)/parser/parser.py

.PHONY: import
import:
	pipenv run python $(PWD)/parser/importer.py

.PHONY: run
run: import parse
