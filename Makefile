.PHONY: install
install:
	pipenv install

.PHONY: parser
parse:
	pipenv run python $(PWD)/parser/parser.py

.PHONY: importer
import:
	pipenv run python $(PWD)/parser/importer.py

.PHONY: run
run: importer parser
