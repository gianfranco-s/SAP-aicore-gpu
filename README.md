There was a syntax error in serve.py. I removed `@app.before_first_request`

1. Create and push a new docker image
2. Update yaml file


1.
cd server
sudo docker login docker.io
sudo docker build -t docker.io/gsalomone/movie-review-clf-serve:0.0.2 .
sudo docker push docker.io/gsalomone/movie-review-clf-serve:0.0.2