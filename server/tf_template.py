import logging

import numpy as np

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

logging.basicConfig(format="%(asctime)s:%(name)s:%(levelname)s - %(message)s", level=logging.INFO)

class KerasModel:
   """ Placeholder class, to avoid importing from keras """


class Model:
    """ Load model for inferencing"""
    def __init__(self, source_path='/content'):
        self.source_path = source_path
        self.model = None
        self.load_model()

    def load_model(self, filename: str = 'model.h5') -> KerasModel:
        self.model = load_model(f'{self.source_path}/{filename}')
        self.model.summary()
        return self.model

    def predict(self, seq: np.ndarray) -> str:
        """
        Parameters
            seq : numpy.ndarray
            <1, MAX_PAD_LEN>
        """
        return self.model.predict(seq)


class TextProcess:
    """ Pre and post text processor"""
    def __init__(self, source_path: str = '/content'):
        self.source_path = source_path
        self.set_pad_len()
        self.encoder = None 
        self.load_label_encoder()

        self.load_tokenizer()

    def set_pad_len(self, filename: str = 'max_pad_len.txt') -> None:
        with open(f'{self.source_path}/{filename}') as file:
            self.max_pad_len = int(file.read())

    def load_label_encoder(self, filename: str = 'label_encoded_classes.npy') -> None:
        self.encoder = LabelEncoder()
        self.encoder.classes_ = np.load(f'{self.source_path}/{filename}')
        # return self.encoder  # I believe this can be removed (it never gets assigned to anything)

    def load_tokenizer(self, filename: str = 'tokens.json') -> None:
        # read as <str> from JSON file
        with open(f'{self.source_path}/{filename}', 'r') as tokenfile:
            tokens_info = tokenfile.read()
        
        self.tokenizer = tokenizer_from_json(tokens_info)
        # return self.tokenizer  # I believe this can be removed (it never gets assigned to anything)

    def pre_process(self, sentence: str) -> np.ndarray:
        """converts sentence to token
        Returns x_seq : numpy.ndarray shape <1, self.max_pad_len>
        """
        x_seq = self.tokenizer.texts_to_sequences(sentence)
        x_seq = pad_sequences(x_seq, maxlen=self.max_pad_len)
        return x_seq

    def post_process(self, prediction: np.ndarray) -> dict:
        """Convert back to orginial class name
        Parameters
            prediction : numpy.ndarray (dtype = float32, shape = (1, n_classes) #n_classes captured within the model
        Returns:
            dict 
                <predicted_class_name, probability>
                ONLY the maximum confident class
        """
        prediction_flatten = prediction.flatten()
        probability_argmax = np.argmax(prediction_flatten)
        probability = prediction_flatten[probability_argmax]
        predicted_class_name = self.encoder.inverse_transform([probability_argmax])[0]
        return {predicted_class_name: float(probability)}
