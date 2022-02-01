import json
import logging

import azure.functions as func

from graphene import ObjectType, String, Boolean, Field, Schema, List

HELP_TEXT = "Please provide an encoded GraphQL data query, e.g. '{ \"query\": \"query { hello }\"}'"


class Query(ObjectType):
    hello = String()

    def resolve_hello(query, info):
        return "Hi there!"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Generate schema
    schema = Schema(query=Query)

    # Extract query from request
    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(HELP_TEXT, status_code=400)
    if "query" not in data:
        return func.HttpResponse(HELP_TEXT, status_code=400)

    # Execute query
    result = schema.execute(data["query"]).to_dict()

    # Return result
    return func.HttpResponse(
        json.dumps(result),
        mimetype="appication/json")
