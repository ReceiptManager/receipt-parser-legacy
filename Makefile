.PHONY: install
install:
	pipenv install

.PHONY: parse
parse:
	pipenv run python parser.py

.PHONY: import
import:
	pipenv run python importer.py

.PHONY: run
run: importer parse
