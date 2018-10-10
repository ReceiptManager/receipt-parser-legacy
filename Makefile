.PHONY: install
install:
	pipenv install

.PHONY: parser
parser:
	pipenv run python parser.py

.PHONY: importer
importer:
	pipenv run python importer.py

.PHONY: run
run: importer parser
