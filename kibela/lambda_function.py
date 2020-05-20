import os
import json

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

team = os.environ.get('KIBELA_TEAM')
token = os.environ.get('KIBELA_TOKEN')
folder_id = os.environ.get('FOLDER_ID')
api_endpoint = 'https://{}.kibe.la/api/v1'.format(team)


def getPages():

    http_transport = RequestsHTTPTransport(
        url=api_endpoint,
        headers={
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'},
        use_json=True
    )

    client = Client(
        transport=http_transport,
        fetch_schema_from_transport=False,
    )

    query = gql('''
        query HelloKibela {
            notes(first: 10, orderBy: { field: CONTENT_UPDATED_AT, direction: DESC }, folderId: "{}") {
                edges {
                    node {
                        title
                        publishedAt
                        content
                    }
                }
            }
        }
        '''.format(folder_id)

    res=client.execute(query)
    return res


def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(getPages())
    }
