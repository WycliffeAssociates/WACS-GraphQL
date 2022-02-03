# pylint: disable=invalid-name

""" Provides a GraphQL interfact to the WACS WA-Catalog """

from dataclasses import dataclass
import json
import logging
import re
import typing

from graphene import ObjectType, String, Boolean, Field, Schema, List  # type: ignore # pylint: disable=import-error
import azure.functions as func  # type: ignore # pylint: disable=import-error
import requests

HELP_TEXT = (
    "Please provide an encoded GraphQL data query, e.g.\n"
    """curl -X POST -H "Content-Type: application/json" """
    """-d '{"query": "{ wacsCatalog { languageCode resourceType url } }"}' """
    """https://wacs-graphql.azurewebsites.net/api/WACS_GraphQL?code=<function access code>"""
)

RESOURCE_NAME_REGEX = re.compile(r"^([^_]+)_([^_]+)$")


@dataclass
class Repository:

    """A repository on DCS or WACS."""

    user_id: str
    repo_id: str
    url: str
    create_date: str
    update_date: str


def gitea_orgs_repos(server: str, org: str) -> typing.List[Repository]:
    """Reads list of organization's repos from server.  Read until we run out of pages."""
    api_url = f"{server}/api/v1"
    repos: typing.List[Repository] = []
    page_num = 0
    while True:

        # Get next page of repos.
        page_num += 1
        request_url = f"{api_url}/orgs/{org}/repos?page={page_num}"
        response = requests.get(request_url)
        response.raise_for_status()
        data = response.json()
        num_items = len(data)
        logging.info("Received %d repo(s) from %s.", num_items, server)

        # Stop when no more items
        if num_items == 0:
            logging.info("No more repos, done.")
            break

        # Process repos
        for json_repo in data:
            repo = Repository(
                user_id=json_repo["owner"]["login"],
                repo_id=json_repo["name"],
                url=json_repo["html_url"],
                create_date=json_repo["created_at"],
                update_date=json_repo["updated_at"],
            )
            repos.append(repo)

    return repos


class Resource(ObjectType):
    # pylint: disable=too-few-public-methods

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
        logging.info("resolve_wacs_catalog()")
        resources: typing.List[Resource] = []
        repos = gitea_orgs_repos(
            "https://content.bibletranslationtools.org", "WA-Catalog"
        )

        for repo in repos:
            match = RESOURCE_NAME_REGEX.match(repo.repo_id)
            if match:
                resource = Resource(
                    match.group(1), match.group(2), repo.url
                )
                resources.append(resource)

        return resources


def main(req: func.HttpRequest) -> func.HttpResponse:

    """main function (called by Azure)"""

    logging.info("Received HTTP request.")

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
