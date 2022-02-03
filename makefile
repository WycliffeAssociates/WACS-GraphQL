.PHONY: start run-query-local run-query-remote edit lint lint-watch

start:
	func start --verbose

run-query-local:
	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' \
		http://localhost:7071/api/WACS_GraphQL \
		| jq .

run-query-remote:
	curl \
		-X POST \
		-H "Content-Type: application/json" \
		-H "x-functions-key: $${WACS_GRAPHQL_FUNCTION_KEY}" \
		-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' \
		https://wacs-graphql.azurewebsites.net/api/WACS_GraphQL \
		| jq .

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
