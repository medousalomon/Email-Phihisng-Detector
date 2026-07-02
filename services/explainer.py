import numpy as np
import re
import html
from lime.lime_text import LimeTextExplainer

from services.predictor import model, tokenizer
from services.text_preprocess import clean_text
from tensorflow.keras.preprocessing.sequence import pad_sequences


MAX_LEN = 200


def predict_proba(texts):
    cleaned = [clean_text(t) for t in texts]

    sequences = tokenizer.texts_to_sequences(cleaned)

    padded = pad_sequences(
        sequences,
        maxlen=MAX_LEN,
        padding="post"
    )

    preds = model.predict(
        padded,
        verbose=0
    )

    return np.hstack((1 - preds, preds))


def explain_email(email_text, num_features=10):
    explainer = LimeTextExplainer(
        class_names=[
            "LEGITIMATE",
            "PHISHING"
        ]
    )

    explanation = explainer.explain_instance(
        email_text,
        predict_proba,
        num_features=num_features
    )

    return explanation.as_list()




def generate_highlighted_html(email_text, explanation):

    safe_text = html.escape(email_text)

    sorted_explanation = sorted(
        explanation,
        key=lambda x: len(x[0]),
        reverse=True
    )

    for word, weight in sorted_explanation:

        escaped_word = html.escape(word)

        color = "#ff4b4b" if weight > 0 else "#4CAF50"

        highlighted_word = (
            f'<span style="background-color:{color}; color:white; '
            f'padding:2px 5px; border-radius:4px;">'
            f'{escaped_word}</span>'
        )

        pattern = r"\b" + re.escape(escaped_word) + r"\b"

        safe_text = re.sub(
            pattern,
            highlighted_word,
            safe_text,
            flags=re.IGNORECASE
        )

    return safe_text.replace("\n", "<br>")