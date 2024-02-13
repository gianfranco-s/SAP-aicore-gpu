# -*- coding: utf-8 -*-
"""
Inference script that extends from the base infer interface
"""
import os
import logging

import tensorflow as tf

from flask import Flask
from flask import request as call_request

from tf_template import Model, TextProcess


app = Flask(__name__)

text_process = None
model = None


@app.before_first_request
def init():
    """
    Load the model if it is available locally
    """

    # import logging  # I believe we can remove this
    logging.info(f"Num GPUs Available: {len(tf.config.list_physical_devices('GPU'))}")

    global text_process, model
    
    serve_files_paths = os.environ['SERVE_FILES_PATH']

    # Load text pre and post processor
    text_process = TextProcess(serve_files_paths)
    text_process.max_pad_len

    # load model
    model = Model(serve_files_paths)

    return None


@app.route("/v1/predict", methods=["POST"])
def predict():
    """
    Perform an inference on the model created in initialize

    Returns:
        String prediction of the label for the given test data
    """
    global model, text_process

    input_data = dict(call_request.json)
    text = str(input_data['text'])

    # Log first
    logging.info(f"Requested text: {text}")

    # Prediction
    prediction = model.predict(
        text_process.pre_process([text]) # Important to pass as list
    )

    logging.info(f"Prediction: {prediction}")

    return text_process.post_process(prediction)


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", debug=True, port=9001)

# curl --location --request POST 'http://localhost:9001/v1/predict' --header 'Content-Type: application/json' --data-raw '{"text": "A restaurant with great ambiance"}'