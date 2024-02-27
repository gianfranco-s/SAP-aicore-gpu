import logging
import os

import numpy as np

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

FORMAT = "%(asctime)s:%(name)s:%(levelname)s - %(message)s"
# Use filename="file.log" as a param to logging to log to a file
logging.basicConfig(format=FORMAT, level=logging.INFO)

SERVE_PATH = os.environ['SERVE_FILES_PATH']


class Model:
    def __init__(self, source_path: str = SERVE_PATH) -> None:
        self.source_path = source_path
        self.model = None
        self.__load_model()

    def __load_model(self, filename: str = 'model.h5') -> None:
        model_filepath = os.path.join(self.source_path, filename)
        self.model = load_model(model_filepath)

    def predict(self, seq):
        '''
        Parameters
        ---
        seq : numpy.ndarray
          <1, MAX_PAD_LEN>
        '''
        print('-------------')
        print(type(seq))
        print(type(self.model.predict(seq)))
        return self.model.predict(seq)


class TextProcess:
    """Text Process - pre and post"""
    def __init__(self, source_path: str = SERVE_PATH) -> None:
        self.source_path = source_path

        self.max_pad_len = None
        self.__get_pad_len()

        self.encoder = None
        self.__load_label_encoder()

        self.tokenizer = None
        self.__load_tokenizer()

    def __get_pad_len(self, filename: str = 'max_pad_len.txt') -> None:
        pad_len_filepath = os.path.join(self.source_path, filename)
        with open(pad_len_filepath) as file:
          self.max_pad_len = int(file.read())

    def __load_label_encoder(self, filename: str = 'label_encoded_classes.npy') -> None:
        encoded_classes_path = os.path.join(self.source_path, filename)
        self.encoder = LabelEncoder()
        self.encoder.classes_ = np.load(encoded_classes_path)

    def __load_tokenizer(self, filename: str = 'tokens.json') -> None:
        tokenizer_path = os.path.join(self.source_path, filename)
        with open(tokenizer_path, 'r') as tokenfile:
          tokens_info = tokenfile.read()
        self.tokenizer = tokenizer_from_json(tokens_info)

    def pre_process(self, sentence: str) -> np.ndarray:
        '''Converts sentence to token
        Returns
        ---
        x_seq : numpy.ndarray shape <1, self.max_pad_len>
        '''
        x_seq = self.tokenizer.texts_to_sequences([sentence])
        return pad_sequences(x_seq, maxlen=self.max_pad_len)

    def post_process(self, prediction: np.ndarray) -> dict:
        '''Convert back to orginial class name

        Parameters
          prediction: numpy.ndarray (dtype = float32, shape = (1, n_classes) #n_classes captured within the model
        
        Returns:
          dict 
            <predicted_class_name, probability>
            ONLY the maximum confident class
        '''
        prediction_flatten = prediction.flatten()
        probability_argmax = np.argmax(prediction_flatten)
        probability = prediction_flatten[probability_argmax]

        predicted_class_name = self.encoder.inverse_transform([probability_argmax])[0]
        return {predicted_class_name: float(probability)}
