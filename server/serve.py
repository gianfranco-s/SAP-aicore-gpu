from flask import Flask
from flask import request as call_request

from tf_template import Model, TextProcess, AVAILABLE_GPUS

app = Flask(__name__)


def initialize_app():
    
    app.logger.info(f"Num GPUs Available: {len(AVAILABLE_GPUS)}")

    text_process = TextProcess()
    model = Model()

    return text_process, model


@app.route("/v1/predict", methods=["POST"])
def predict() -> str:
    text_process = app.config['text_process']
    model = app.config['model']

    input_data = dict(call_request.json)
    text = str(input_data['text'])

    app.logger.info(f'Requested text: {text}')
    prediction = model.predict(
        text_process.pre_process(text)
    )

    app.logger.info(f"Prediction: {prediction}")

    return text_process.post_process(prediction)


if __name__ == "__main__":
    with app.app_context():
        text_process, model = initialize_app()

    app.config['text_process'] = text_process
    app.config['model'] = model
    app.run(host="0.0.0.0", debug=True, port=9001)

# curl --location --request POST 'http://localhost:9001/v1/predict' --header 'Content-Type: application/json' --data-raw '{"text": "A restaurant with great ambiance"}'
