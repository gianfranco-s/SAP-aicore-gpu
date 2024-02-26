import json
import os

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from dotenv import load_dotenv


BASEDIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
github_token_file = BASEDIR + '/github.creds'
docker_token_file = BASEDIR + '/docker.creds'

load_dotenv(github_token_file)
load_dotenv(docker_token_file)

GITHUB_USER = os.getenv('GITHUB_USER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

DOCKER_USER = os.getenv('DOCKER_USER')
DOCKER_TOKEN = os.getenv('DOCKER_TOKEN')

AWS_CREDENTIALS_PATH = os.path.expanduser("~/.aws/credentials")

def get_conn_details(path_to_credentials: str = BASEDIR + '/default_aicore.json') -> dict:
    with open(path_to_credentials, 'r') as f:
        credentials = json.load(f).get('credentials')

    return {
        'base_url': credentials.get('serviceurls').get('AI_API_URL') + '/v2',
        'auth_url': credentials.get('url') + "/oauth/token",
        'client_id': credentials.get('clientid'),
        'client_secret': credentials.get('clientsecret'),
    }


def onboard_repository(github_repo_url: str,
                       github_account_usr: str,
                       github_token: str,
                       project_name: str,
                       ai_core_client: AICoreV2Client,
                       ) -> str:
    """ This function allows to clarify naming of attributes. """
    # https://developers.sap.com/tutorials/ai-core-helloworld.html#:~:text=STEP%203-,Onboard%20GitHub%20to%20SAP%20AI%20Core,-SAP%20AI%20Launchpad
    response = ai_core_client.repositories.create(
        name=project_name,
        url=github_repo_url,
        username=github_account_usr,
        password=github_token)
    return response.message


def onboard_docker(docker_registry_name: str,
                   docker_user: str,
                   docker_token: str,
                   ai_core_client: AICoreV2Client,
                   docker_url: str = 'https://index.docker.io') -> str:
    docker_auth_data = {
        'auths': {
            docker_url: {
                'username': docker_user,
                'password': docker_token
            }
        }
    }

    response = ai_core_client.docker_registry_secrets.create(
        name = docker_registry_name,
        data = {
            ".dockerconfigjson": json.dumps(docker_auth_data)
        }
    )
    return response.message


def show_repositories(ai_core_client: AICoreV2Client) -> None:
    response = ai_core_client.repositories.query()

    for repository in response.resources:
        message = f"Name: {repository.name}\nURL: {repository.url}\nStatus: {repository.status}\n"
        print(message)


def show_docker_registries(ai_core_client: AICoreV2Client) -> None:
    response = ai_core_client.docker_registry_secrets.query()
    
    for secret_name in response.resources:
        print(secret_name)
