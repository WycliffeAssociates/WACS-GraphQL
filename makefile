.PHONY: start run-query edit lint lint-watch

start:
	func start

run-query:
	curl -X POST -H "Content-Type: application/json" -d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' http://localhost:7071/api/WACS_GraphQL  | jq .

edit:
	$(EDITOR) WACS_GraphQL/__init__.py makefile

lint:
	mypy --check-untyped-defs WACS_GraphQL/__init__.py
	pylint --output-format=colorized WACS_GraphQL/__init__.py

lint-watch:
	while inotifywait -e close_write,moved_to,create WACS_GraphQL; do \
		clear; \
		$(MAKE) lint; \
		done
