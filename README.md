---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import json

from configparser import ConfigParser

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_api_client_sdk.exception import AIAPINotFoundException, AIAPIServerException, AIAPIInvalidRequestException

from sapaicore_utils import (AWS_CREDENTIALS_PATH,
                             DOCKER_TOKEN,
                             DOCKER_USER,
                             get_conn_details,
                             GITHUB_TOKEN,
                             GITHUB_USER,
                             onboard_repository,
                             onboard_docker,
                             show_docker_registries,
                             show_repositories,)

conn_details = get_conn_details()
ai_core_client = AICoreV2Client(**conn_details)
```

## Step 0. Onboard a repository and Docker account


### GitHub repository
We'll need a GitHub username and token

```python
# First, let's see which repositories have been onboarded
show_repositories(ai_core_client)
```

```python
PROJECT_NAME = 'gsalomone-tf-gpu'
github_repo_url = 'https://github.com/gianfranco-s/SAP-aicore-gpu'
```

```python
# If project does not exist, AIAPINotFoundException is raised when `get()` is invoked
try:
    ai_core_client.repositories.get(PROJECT_NAME)
    print('Repository already exists')

except AIAPINotFoundException:
    onboard_repository(github_repo_url,
                    GITHUB_USER,
                    GITHUB_TOKEN,
                    PROJECT_NAME,
                    ai_core_client)
    print('Repository created')
```

### Docker account

```python
# First, let's see which registries have been onboarded
show_docker_registries(ai_core_client)
```

```python
docker_registry_name = 'gsalomone-docker'

# If project does not exist, AIAPINotFoundException is raised when `get()` is invoked
try:
    ai_core_client.docker_registry_secrets.get(docker_registry_name)
    print('Docker registry already exists')

except AIAPINotFoundException:
    onboard_docker(docker_registry_name, DOCKER_USER, DOCKER_TOKEN, ai_core_client)
    print('Docker registry created')
```

## Step 1. Create workspace
Using default resource group because when I tried to create `tf-demo`, I got the message "Resource Group cannot be created for free tier tenant"

```python
try:
    response = ai_core_client.resource_groups.create("tf-demo")

except AIAPIServerException as e:
    print(e)
```

```python
def show_resource_groups() -> None:
    response = ai_core_client.resource_groups.query()

    for rg in response.resources:
        print(rg.resource_group_id)

show_resource_groups()
```

## Step 2: upload model files to AWS S3
Create bucket
```
aws s3api create-bucket --bucket gsalomone-celestial-bucket --region us-east-1
```

Upload files
```
cd tf_files
aws s3 cp model.h5 s3://gsalomone-celestial-bucket/movie-clf/model/
aws s3 cp max_pad_len.txt s3://gsalomone-celestial-bucket/movie-clf/model/
aws s3 cp label_encoded_classes.npy s3://gsalomone-celestial-bucket/movie-clf/model/
aws s3 cp tokens.json s3://gsalomone-celestial-bucket/movie-clf/model/
```

Check files
```
aws s3 ls s3://gsalomone-celestial-bucket/movie-clf/model/
```

Alternatively, it can be done using the AWS SDK

```python
import boto3


def file_exists_in_s3(bucket_name: str, s3_key: str, file_name: str) -> bool:
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket_name, Key=s3_key + file_name)
        return True
    except Exception as e:
        return False


def upload_file_to_s3(file_dir: str, file_name: str, bucket_name: str, s3_key: str) -> None:
    if file_exists_in_s3(bucket_name, s3_key, file_name):
        print(f'file {file_name} already exists in key: {s3_key}, bucket: {bucket_name}')
        return

    try:
        s3 = boto3.client('s3')
        s3.upload_file(file_dir + file_name, bucket_name, s3_key + file_name)
        print(f"File uploaded successfully to S3 bucket: {bucket_name} with key: {s3_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")


bucket_name = 'gsalomone-celestial-bucket'
s3_key = 'movie-clf/model/'
file_dir = 'tf_files/'
```

```python
upload_file_to_s3(file_dir, 'model.h5', bucket_name, s3_key)
upload_file_to_s3(file_dir, 'max_pad_len.txt', bucket_name, s3_key)
upload_file_to_s3(file_dir, 'label_encoded_classes.npy', bucket_name, s3_key)
upload_file_to_s3(file_dir, 'tokens.json', bucket_name, s3_key)
```

## Step 3: connect AWS S3 to SAP AI Core
Keep in mind that the attribute `endpoint` only uses the availability zone only if the bucket resides outside `us-east-1`
Examples:
- if region is `us-east-one`, endpoint is `s3.amazonaws.com`
- if region is `eu-central-1`, endpoint is `s3-eu-central-1.amazonaws.com`

```python
config = ConfigParser()
config.read(AWS_CREDENTIALS_PATH)

aws_access_key_id = config.get('default', 'aws_access_key_id')
aws_secret_access_key = config.get('default', 'aws_secret_access_key')

aws_az = 'us-east-1'
object_store_name = 'gs-tf-gpu-tutorial-secret'
```

```python
def create_s3_object_store(object_store_name: str, bucket_name: str, s3_key: str, aws_az: str) -> str:
    response = ai_core_client.object_store_secrets.create(
        resource_group = 'default',
        type = "S3",
        name = object_store_name,
        path_prefix = s3_key,
        endpoint = f"s3.{aws_az}.amazonaws.com",  # https://docs.aws.amazon.com/general/latest/gr/s3.html
        bucket = bucket_name,
        region = aws_az,
        data = {
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
        }
    )

    return response.message

res = create_s3_object_store(object_store_name, 'gsalomone-celestial-bucket', s3_key='movie-clf', aws_az=aws_az)
res
```

## Step 4: register model as Artifact
Let's follow the tutorial to the letter.

Spoiler: it will not work.
```
Invalid Request, Could not create Artifact due to invalid Scenario ID <id-here>. Please check the Scenario ID.
```
**We'll follow step 6 first**

```python
# Register model as artifact
from ai_core_sdk.models import Artifact

def create_model(model_name: str, object_store_name: str, scenario_id: str, description: str) -> str:
    """Create artifact as model
    
    Keyword arguments:
    model_name -- self explanatory
    object_store_name -- s3 object store
    scenario_id -- taken form the yaml file, found under `scenarios.ai.sap.com/id`
    Return: return_description
    """
    
    response = ai_core_client.artifact.create(
        resource_group = 'default',
        name = model_name,
        kind = Artifact.Kind.MODEL,
        url = f"ai://{object_store_name}/model",
        scenario_id = scenario_id,
        description = description
    )
    return response.message
```

```python
# If you run this code AFTER creating the scenario, it will work ok
# because scenario_id will already be available

try:
    msg = create_model(model_name='gsalomone-model',
                       scenario_id='tf-text-clf',
                       description='Review Classification Model',
                       object_store_name=object_store_name,)

    print(msg)
except AIAPIInvalidRequestException as e:
    print(e)
```

### Step 4 -> Step 6: we need to set up the scenario_id FIRST
It turns out that `scenario_id` is created from the yaml file. So we'll move to step 6 of the tutorial

- Copy [`serving_executable.yaml`](https://raw.githubusercontent.com/sap-tutorials/Tutorials/master/tutorials/ai-core-tensorflow-byod/files/workflow/serving_executable.yaml)
- set `resourcePlan` to `infer.s` which will enable GPU. ATTENTION: free tier only allows for `starter`
- set `imagePullSecrets > name` to the appropriate docker registry secret. In this tutorial you'll find it in variable `docker_registry_name`
- set `containers > image` is set to `"docker.io/DOCKER_USER/movie-review-clf-serve:0.0.1"`


### Step 4 -> Step 7: sync with SAP AI Core
- Push `serving_executable.yaml` to GitHub
- Create the application in SAP AI Core
- Check for typos in yaml file `executables.ai.sap.com/name: "serve-executuable"` -> `executables.ai.sap.com/name: "serve-executable"`


```python
# Create application
application_name = 'gsalomone-tf-app'

try:
    response = ai_core_client.applications.create(
        application_name = application_name,
        revision = "HEAD",
        repository_url = github_repo_url,
        path = "tf-text-classifier"  # path to the yaml file in the repository
    )
except AIAPIServerException as e:
    reason = json.loads(e.error_message).get('reason')
    print(f'Application cannot be created because: {reason}')
```

```python
response = ai_core_client.applications.get_status(application_name=application_name)
print(response.message)

for workflow_sync_status in response.sync_ressources_status:
    print(f'\napplication status: ', workflow_sync_status.status)
    print(f'workflow message: ', workflow_sync_status.message)
    print(f'application name (from yaml file): ', workflow_sync_status.name)
```

### Step 4 -> Step 4: NOW register model as artifact

```python
SCENARIO_ID = 'tf-text-clf'  # Remember to copy it from the yaml file: `scenarios.ai.sap.com/id`
msg = create_model(model_name='gsalomone-model',
                    scenario_id=SCENARIO_ID,
                    description='Review Classification Model',
                    object_store_name=object_store_name,)

print(msg)
```

```python
# Show artifacts
artifacts = ai_core_client.artifact.query(resource_group='default')

artifact_resources = artifacts.resources

for resource in artifact_resources:
    print(f"artifact_id: {resource.id}")
    print(f"created_at: {resource.created_at}")
    print(f"execution_id: {resource.execution_id}")
    print(f"kind: {resource.kind}")
    print(f"name: {resource.name}")
    print(f"scenario_id: {resource.scenario_id}")
    print(f"url: {resource.url}\n")
```

```python
# Latest artifact is apparently at the top of the list, so let's define
artifact_resources = ai_core_client.artifact.query(resource_group='default').resources
artifact_id = artifact_resources[0].id
artifact_id
```

```python
# Just showing another way to get artifact data
from pprint import pprint

res = ai_core_client.artifact.get(artifact_id=artifact_id, resource_group='default')
pprint(res.__dict__)
```

## Step 5: set up serving code
```
cd server
sudo docker login docker.io  # Password is the Personal Access Token
sudo docker build -t docker.io/gsalomone/movie-review-clf-serve:0.0.1 .
sudo docker push docker.io/gsalomone/movie-review-clf-serve:0.0.1
```
- Modify requirements to install latest versions
- Use flag `--ignore-installed` in Dockerfile



## Step 8: create configuration

```python

# Create configuration
from ai_core_sdk.models import InputArtifactBinding

EXECUTABLE_ID = "tf-text-clf-serve"  # It's the (first) `name` key in the yaml file

response = ai_core_client.configuration.create(
    name = "gsalomone-tf-gpu-conf",
    resource_group = "default",
    scenario_id = SCENARIO_ID,
    executable_id = EXECUTABLE_ID,
    input_artifact_bindings = [
        InputArtifactBinding(key="modelArtifact", artifact_id = artifact_id), # Change artifact id
    ]
)

print(response.__dict__)
config_id = response.id
```

```python
configurations = ai_core_client.configuration.query(resource_group='default')

for resource in configurations.resources:
    print(resource.__dict__)
```

```python
configuration_details = configurations.resources[0]
configuration_details.__dict__
```

## Step 9: start deployment

```python
# Again, apparently the latest resource appears at the top, so
configurations = ai_core_client.configuration.query(resource_group='default')
configuration_id = configurations.resources[0].id
print(f'{configuration_id=}')

response = ai_core_client.deployment.create(
    resource_group = "default",
    configuration_id = configuration_id
)
```

```python
response.__dict__
```

```python
deployments = ai_core_client.deployment.query(resource_group="default")

# Following what we've learned about the query method:
deployment_id = deployments.resources[0].id
deployment_id
```

```python
# Check deployment status
# This may take 2-3 minutes to change state from UNKNOWN > PENDING > RUNNING.

response = ai_core_client.deployment.get(resource_group="default", deployment_id=deployment_id)

print("Status: ", response.status)
print('*'*80)
print(response.__dict__)
```

```python
logs = ai_core_client.deployment.query_logs(deployment_id=deployment_id, resource_group='default').data.result

for log in logs:
    print(log.__dict__)
```

```python
query_text = "The story after the interval had predictable twist-turns."
deployment_id = deployment_id

custom_endpoint = "/v1/predict"

prediction = ai_core_client.rest_client.post(
    resource_group = "default",
    path = "/inference/deployments/" + deployment_id + custom_endpoint,
    body = {
        "text": query_text
    }
)

print(prediction)
```

<!-- #region -->
## Server updates
If there are changes needed on the server


1. Create and push a new docker image
```
cd server
sudo docker login docker.io
sudo docker build -t docker.io/gsalomone/movie-review-clf-serve:<new_version> .
sudo docker push docker.io/gsalomone/movie-review-clf-serve:<new_version>
```

2. Change version in yaml file
```
image: "docker.io/gsalomone/movie-review-clf-serve:<new_version>"
```

3. Push yaml file to branch main in repo
```
git commit -am "Updated version in yaml file to <new_version>" && git push
```

4. Rerun from `Create configuration`
<!-- #endregion -->
