.PHONY: install
install:
	poetry install

.PHONY: parse
parse:
	poetry run

.PHONY: import
import:
	poetry run python receipt_parser_core/enhancer.py

.PHONY: run
run: import parse

.PHONY: docker-build
docker-build:
	docker build -t mre0/receipt_parser .

.PHONY: docker-push
docker-push:
	docker push mre0/receipt_parser

.PHONY: docker-run
docker-run:
	docker run -v `pwd`/data/img:/app/data/img mre0/receipt_parser

.PHONY: test
test:
	poetry run pytest 

.PHONY: clean
clean:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: publish
publish:
	poetry publish --build