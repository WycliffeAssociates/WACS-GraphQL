.PHONY: start run-query-local run-query-remote edit lint lint-watch

start:
	test -n "$(WACS_API_URL)" # Please set $$WACS_API_URL
	func start --verbose

run-query-local:
	curl \
		-i \
		-X POST \
		-H "Content-Type: application/json" \
		-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' \
		http://localhost:7071/api/WACS_GraphQL

run-query-prod:
	test -n "$(WACS_GRAPHQL_FUNCTION_KEY_PROD)" # $$WACS_GRAPHQL_FUNCTION_KEY_PROD
	curl \
		-i \
		-X POST \
		-H "Content-Type: application/json" \
		-H "x-functions-key: $${WACS_GRAPHQL_FUNCTION_KEY_PROD}" \
		-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' \
		https://wacs-graphql.walink.org/api/WACS_GraphQL

run-query-dev:
	test -n "$(WACS_GRAPHQL_FUNCTION_KEY_DEV)" # $$WACS_GRAPHQL_FUNCTION_KEY_DEV
	curl \
		-i \
		-X POST \
		-H "Content-Type: application/json" \
		-H "x-functions-key: $${WACS_GRAPHQL_FUNCTION_KEY_DEV}" \
		-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' \
		https://wacs-graphql-dev.walink.org/api/WACS_GraphQL

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
