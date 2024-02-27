import os
import logging

import tensorflow as tf

from flask import Flask
from flask import request as call_request

from tf_template import Model, TextProcess

app = Flask(__name__)


def init():
    available_gpus = tf.config.list_physical_devices('GPU')
    logging.info(f"Num GPUs Available: {len(available_gpus)}")

    text_process = TextProcess()
    model = Model()

    return text_process, model


@app.route("/v1/predict", methods=["POST"])
def predict() -> str:
    text_process = app.config['text_process']
    model = app.config['model']

    input_data = dict(call_request.json)
    text = str(input_data['text'])

    logging.info(f'Requested text: {text}')
    prediction = model.predict(
        text_process.pre_process(text)
    )

    logging.info(f"Prediction: {prediction}")

    return text_process.post_process(prediction)


if __name__ == "__main__":
    text_process, model = init()
    app.config['text_process'] = text_process
    app.config['model'] = model
    app.run(host="0.0.0.0", debug=True, port=9001)

# curl --location --request POST 'http://localhost:9001/v1/predict' --header 'Content-Type: application/json' --data-raw '{"text": "A restaurant with great ambiance"}'