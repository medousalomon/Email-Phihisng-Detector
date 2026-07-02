import pandas as pd
import pickle

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


# LOAD DATA

def load_data(path):
    df = pd.read_csv(path)
    return df



# TOKENIZATION

def tokenize_text(texts, vocab_size=10000, max_len=200):
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)

    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post')

    return tokenizer, padded_sequences



# SAVE TOKENIZER

def save_tokenizer(tokenizer, path):
    with open(path, 'wb') as f:
        pickle.dump(tokenizer, f)



# MAIN

if __name__ == "__main__":
    input_path = "D:\\Project Masters\\phishing detection system\\data\\processed\\merged_emails.csv"

    tokenizer_path = "D:\\Project Masters\\phishing detection system\\models\\tokenizer.pkl"
    output_features_path = "D:\\Project Masters\\phishing detection system\\data\\processed\\features.npy"
    output_labels_path = "D:\\Project Masters\\phishing detection system\\data\\processed\\labels.npy"

    df = load_data(input_path)

    print("Tokenizing text...")

    tokenizer, X = tokenize_text(df['text'])

    y = df['label'].values

    # Save everything
    save_tokenizer(tokenizer, tokenizer_path)

    import numpy as np
    np.save(output_features_path, X)
    np.save(output_labels_path, y)

    print("Feature extraction complete!")