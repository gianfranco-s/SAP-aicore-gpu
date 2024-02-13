## Notes

### 1. Create workspace
Using default resource group because "Resource Group cannot be created for free tier tenant"

### 2. Upload model files to AWS S3
Need to create an S3 bucket

### 3. Create object store to connect AWS S3 to SAP AI Core
Need AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### 4. Create workflow to serve model
This is step 6 from the tutorial.
It turns out that `scenario_id` is created from the yaml file.

### 5. Sync workflow from GitHub to SAP AI Core
This is step 7 from the tutorial.
Check for typos in yaml file
`executables.ai.sap.com/name: "serve-executuable"` -> `executables.ai.sap.com/name: "serve-executable"`

### 6. Register model as artifact
This is step 4 from the tutorial.

### 7. Set up serving code
cd server
sudo docker login docker.io  # Password is the Personal Access Token
sudo docker build -t docker.io/gsalomone/movie-review-clf-serve:0.0.1 .
sudo docker push docker.io/gsalomone/movie-review-clf-serve:0.0.1  
