from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

from services.text_preprocess import clean_text

# Load model
model = load_model("model/phishing_model.h5")

# Load tokenizer
with open("model/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

MAX_LEN = 100


def predict_email(email_text):

    cleaned = clean_text(email_text)

    sequence = tokenizer.texts_to_sequences(
        [cleaned]
    )

    padded = pad_sequences(
        sequence,
        maxlen=MAX_LEN
    )

    prediction = model.predict(
        padded,
        verbose=0
    )[0][0]

    if prediction >= 0.5:

        label = "PHISHING"
        confidence = prediction

    else:

        label = "LEGITIMATE"
        confidence = 1 - prediction

        print(prediction)
        print(label)

    return label, confidence