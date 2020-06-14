import os
import json

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

team = os.environ.get('KIBELA_TEAM')
token = os.environ.get('KIBELA_TOKEN')
parent_id = os.environ.get('PUBLIC_FOLDER')
api_endpoint = 'https://{}.kibe.la/api/v1'.format(team)


def getPages(target_folder):
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
        query getFolders {{
            folder(id: "{}") {{
                folders(first: 10) {{
                    edges {{
                        node {{
                            name
                            id
                        }}
                    }}
                }}
            }}
        }}
        '''.format(parent_id))

    folders = client.execute(query)['folder']['folders']['edges']
    for folder in folders:
        if folder['node']['name'] == target_folder:
            query = gql('''
                query HelloKibela {{
                    notes(first: 10, orderBy: {{ field: CONTENT_UPDATED_AT, direction: DESC }}, folderId: "{}") {{
                        edges {{
                            node {{
                                title
                                content
                            }}
                        }}
                    }}
                }}
                '''.format(folder['node']['id']))

            res = client.execute(query)
            return json.dumps(res['notes']['edges'])

    return "error: {} folder was not found.".format(target_folder)


def lambda_handler(event, context):
    if 'folder' in event['pathParameters']:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': getPages(event['pathParameters']['folder'])
        }
    else:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': "error: folder name is not specified"
        }
