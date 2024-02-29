## Workflow to get SAP AI Core's service key
1. `cf login`
2. `cf target -o baitcon.development -s default`
3. `cf services | grep aicore`  # To find which aicore services are running. In our case we should only find *default_aicore*
4. `cf service-keys default_aicore`  # To list service keys associated with the service
5. `cf service-key default_aicore <service-key-name> | sed 1,2d > default_aicore2.json`

## Workflow to update serve files
1. Create and push a new docker image
```
cd server
sudo docker login docker.io
sudo docker build -t docker.io/gsalomone/movie-review-clf-serve:0.0.2 .
sudo docker push docker.io/gsalomone/movie-review-clf-serve:0.0.2
```

2. Update yaml file
```
image: "docker.io/gsalomone/movie-review-clf-serve:0.0.2"
```

## Run locally
1. Install requirements
```
cat requirements.txt | xargs poetry add
```

2. Run the local server
```
export SERVE_FILES_PATH=tf_files && python server/serve.py 

# export SERVE_FILES_PATH=../tf_files && gunicorn --chdir server serve:app -b 0.0.0.0:9001
```

1. Test with
```
curl --location --request POST 'http://localhost:9001/v1/predict' --header 'Content-Type: application/json' --data-raw '{"text": "A restaurant with great ambiance"}'
```

Response:
```
{
  "negative": 0.5039926171302795
}
```


## Use jupytext to create the README based on ipynb file
```
jupytext --to markdown README.ipynb
```