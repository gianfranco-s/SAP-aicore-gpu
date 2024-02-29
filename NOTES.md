There was a syntax error in serve.py. I removed `@app.before_first_request`

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