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

Error
```
2024-02-26 19:45:59.134966: I external/local_tsl/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2024-02-26 19:45:59.142055: I external/local_tsl/tsl/cuda/cudart_stub.cc:32] Could not find cuda drivers on your machine, GPU will not be used.
2024-02-26 19:45:59.203156: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2024-02-26 19:46:00.463888: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
2024-02-26 19:46:01.389583: I external/local_xla/xla/stream_executor/cuda/cuda_executor.cc:998] successful NUMA node read from SysFS had negative value (-1), but there must be at least one NUMA node, so returning NUMA node zero. See more at https://github.com/torvalds/linux/blob/v6.0/Documentation/ABI/testing/sysfs-bus-pci#L344-L355
2024-02-26 19:46:01.390202: W tensorflow/core/common_runtime/gpu/gpu_device.cc:2251] Cannot dlopen some GPU libraries. Please make sure the missing libraries mentioned above are installed properly if you would like to use GPU. Follow the guide at https://www.tensorflow.org/install/gpu for how to download and setup the required libraries for your platform.
Skipping registering GPU devices...
2024-02-26 19:46:01,390:root:INFO - Num GPUs Available: 0
Traceback (most recent call last):
  File "/home/gsalomone/Documents/05Baitcon/SAP-aicore-gpu/server/serve.py", line 74, in <module>
    init()
  File "/home/gsalomone/Documents/05Baitcon/SAP-aicore-gpu/server/serve.py", line 32, in init
    text_process = TextProcess(os.environ['SERVE_FILES_PATH'])
  File "/usr/lib/python3.10/os.py", line 680, in __getitem__
    raise KeyError(key) from None
KeyError: 'SERVE_FILES_PATH'
```