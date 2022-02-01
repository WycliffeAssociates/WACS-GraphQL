# pylint: disable=invalid-name

""" Provides a GraphQL interfact to the WACS WA-Catalog """

import json
import logging

import azure.functions as func  # pylint: disable=import-error

from graphene import ObjectType, String, Boolean, Field, Schema, List

HELP_TEXT = (
    "Please provide an encoded GraphQL data query, e.g.\n"
    """curl -X POST -H "Content-Type: application/json" """
    """-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' """
    """http://localhost:7071/api/WACS_GraphQL """
)


class Resource(ObjectType):  # pylint: disable=too-few-public-methods

    """Represents a resource in the WACS WA-Catalog."""

    language_code = String()
    resource_type = String()
    url = String()

    def __init__(self, language_code, resource_type, url):
        super().__init__(self)
        self.language_code = language_code
        self.resource_type = resource_type
        self.url = url


class Query(ObjectType):

    """Index of GraphQL queries."""

    wacs_catalog = List(Resource)

    def resolve_wacs_catalog(self, info):
        # pylint: disable=unused-argument,no-self-use
        """Responds to a wacsCatalog query"""
        resource = Resource(
            "en",
            "ulb",
            "https://content.bibletranslationtools.org/WA-Catalog/en_ulb",
        )
        return [resource]


def main(req: func.HttpRequest) -> func.HttpResponse:

    """main function (called by Azure)"""

    logging.info("Python HTTP trigger function processed a request.")

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
        json.dumps(result), mimetype="appication/json"
    )
